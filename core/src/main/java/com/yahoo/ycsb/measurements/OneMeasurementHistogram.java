/**
 * Copyright (c) 2010 Yahoo! Inc. All rights reserved.                                                                                                                             
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you                                                                                                             
 * may not use this file except in compliance with the License. You                                                                                                                
 * may obtain a copy of the License at                                                                                                                                             
 *
 * http://www.apache.org/licenses/LICENSE-2.0                                                                                                                                      
 *
 * Unless required by applicable law or agreed to in writing, software                                                                                                             
 * distributed under the License is distributed on an "AS IS" BASIS,                                                                                                               
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or                                                                                                                 
 * implied. See the License for the specific language governing                                                                                                                    
 * permissions and limitations under the License. See accompanying                                                                                                                 
 * LICENSE file.                                                                                                                                                                   
 */

package com.yahoo.ycsb.measurements;

import java.io.IOException;
import java.text.DecimalFormat;
import java.util.HashMap;
import java.util.Properties;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicIntegerArray;
import java.util.concurrent.atomic.AtomicLong;

import com.yahoo.ycsb.measurements.exporter.MeasurementsExporter;


/**
 * Take measurements and maintain a histogram of a given metric, such as READ LATENCY.
 *
 * @author cooperb
 */
public class OneMeasurementHistogram extends OneMeasurement {
    public static final String BUCKETS = "histogram.buckets";
    public static final String BUCKETS_DEFAULT = "100000";
    //public static final String BUCKETS_DEFAULT = "1000";

    private AtomicInteger _buckets;
    private AtomicIntegerArray histogram;
    private AtomicInteger histogramoverflow;
    private AtomicInteger operations;
    private AtomicInteger retrycounts;
    private AtomicLong totallatency;

    //keep a windowed version of these stats for printing status
    private AtomicInteger windowoperations;
    private AtomicLong windowtotallatency;

    private AtomicInteger min;
    private AtomicInteger max;
    HashMap<Integer, int[]> returncodes;

    public OneMeasurementHistogram(String name, Properties props) {
        super(name);
        _buckets = new AtomicInteger(Integer.parseInt(props.getProperty(BUCKETS, BUCKETS_DEFAULT)));
        histogram = new AtomicIntegerArray(_buckets.get());
        histogramoverflow = new AtomicInteger(0);
        operations = new AtomicInteger(0);
        retrycounts = new AtomicInteger(0);
        totallatency = new AtomicLong(0);
        windowoperations = new AtomicInteger(0);
        windowtotallatency = new AtomicLong(0);
        min = new AtomicInteger(-1);
        max = new AtomicInteger(-1);
        returncodes = new HashMap<Integer, int[]>();
    }

    /* (non-Javadoc)
      * @see com.yahoo.ycsb.OneMeasurement#reportReturnCode(int)
      */
    public synchronized void reportReturnCode(int code) {
        Integer Icode = code;
        if (!returncodes.containsKey(Icode)) {
            int[] val = new int[1];
            val[0] = 0;
            returncodes.put(Icode, val);
        }
        returncodes.get(Icode)[0]++;
    }

/*
    @Override
    public void reportRetryCount(int count) {
        retrycounts.addAndGet(count);
    }
*/

    /* (non-Javadoc)
      * @see com.yahoo.ycsb.OneMeasurement#measure(int)
      */
    public synchronized void measure(int latency) {
        if (latency / 10 >= _buckets.get()) {
        //if (latency / 1000 >= _buckets.get()) {
            histogramoverflow.incrementAndGet();
        } else {
            histogram.incrementAndGet(latency / 10);
            //histogram.incrementAndGet(latency / 1000);
        }
        operations.incrementAndGet();
        totallatency.addAndGet(latency);
        windowoperations.incrementAndGet();
        windowtotallatency.addAndGet(latency);

        if ((min.get() < 0) || (latency < min.get())) {
            min.set(latency);
        }

        if ((max.get() < 0) || (latency > max.get())) {
            max.set(latency);
        }
    }

/*
    @Override
    public void exportMeasurements(MeasurementsExporter exporter) throws IOException {
        exportGeneralMeasurements(exporter);
        exportMeasurementsPart(exporter);
    }

    @Override
    public void exportMeasurementsPart(MeasurementsExporter exporter) throws IOException {
        //do nothing for this type of measurements
    }
*/
//    private void exportGeneralMeasurements(MeasurementsExporter exporter) throws IOException {
    public void exportMeasurements(MeasurementsExporter exporter) throws IOException {
        exporter.write(getName(), "Operations", operations.get());
        exporter.write(getName(), "Retries", retrycounts.get());
        exporter.write(getName(), "AverageLatency(us)", (((double) totallatency.get()) / ((double) operations.get())));
        exporter.write(getName(), "MinLatency(us)", min.get());
        exporter.write(getName(), "MaxLatency(us)", max.get());

        int opcounter = 0;
        boolean done95th = false;
        boolean done99th = false;
        for (int i = 0; i < _buckets.get(); i++) {
            opcounter += histogram.get(i);
            if ((!done95th) && (((double) opcounter) / ((double) operations.get()) >= 0.95)) {
                exporter.write(getName(), "95thPercentileLatency(us)", i * 10);
                //exporter.write(getName(), "95thPercentileLatency(ms)", i);
                done95th = true;
            }
            if ((!done99th) && (((double) opcounter) / ((double) operations.get()) >= 0.99)) {
                exporter.write(getName(), "99thPercentileLatency(us)", i * 10);
                //exporter.write(getName(), "99thPercentileLatency(ms)", i);
//                break;
                done99th = true; 
            }
            if (((double) opcounter) / ((double) operations.get()) >= 0.999) {
                exporter.write(getName(), "99.9thPercentileLatency(us)", i * 10);
                //exporter.write(getName(), "99thPercentileLatency(ms)", i);
                break;
            }
        }

        for (Integer I : returncodes.keySet()) {
            int[] val = returncodes.get(I);
            exporter.write(getName(), "Return=" + I, val[0]);
        }
    }
    
    @Override
    public String getSummary() {
        if (windowoperations.get() == 0) {
            return "";
        }
        DecimalFormat d = new DecimalFormat("#.##");
        double report = ((double) windowtotallatency.get()) / ((double) windowoperations.get());
        windowtotallatency.set(0);
        windowoperations.set(0);
        return "[" + getName() + " AverageLatency(us)=" + d.format(report) + "]";
    }

}
