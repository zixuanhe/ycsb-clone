package net.thumbtack.test;

import net.spy.memcached.PersistTo;
import net.spy.memcached.ReplicateTo;

import java.io.FileInputStream;
import java.io.IOException;
import java.net.URISyntaxException;
import java.util.Enumeration;
import java.util.Properties;

public class Main {

    private static int curArg = 0;

    private static String host = "127.0.0.1";
    private static int port = 8091;
    private static String bucket = "default";
    private static String user = "";
    private static String password = "";
    private static PersistTo persistTo = PersistTo.ZERO;
    private static ReplicateTo replicateTo = ReplicateTo.ZERO;

    private static long recordCount = 0;
    private static long operationCount = 0;
    private static int threadCount = 0;
    private static long insertStart = 0;
    private static OperationType operationType;

    public static void usageMessage() {
        System.out.println("Usage: java net.thumbtack.test.Main [options]");
        System.out.println("Options:");
        System.out.println("  -host IP: host address (default: 127.0.0.1)");
        System.out.println("  -port n: port (default: 8091)");
        System.out.println("  -user n: user (default: \"\")");
        System.out.println("  -password n: password (default: \"\")");
        System.out.println("  -bucket name: name of the bucket (default: default)");
        System.out.println("  -records n: number of records in DB");
        System.out.println("  -insertstart n: start key number (default: 0)");
        System.out.println("  -operations n: number of read operations");
        System.out.println("  -threads n: number of threads");
        System.out.println("  -optype [insert|read|update]: specified type of operations");
        System.out.println("  -persistto [zero|one|two|three|four|master]: persistence type (default: zero)");
        System.out.println("  -replicateto [zero|one|two|three]: replication type (default: zero)");
    }

    public static void main(String[] args) throws URISyntaxException, IOException, InterruptedException {

        if (args.length == 0) {
            usageMessage();
            System.exit(0);
        }

        while (args[curArg].startsWith("-")) {
            if (args[curArg].equals("-host")) {
                host = readArg(args);
            } else if (args[curArg].equals("-port")) {
                port = Integer.parseInt(readArg(args));
            } else if (args[curArg].equals("-user")) {
                user = readArg(args);
            } else if (args[curArg].equals("-password")) {
                password = readArg(args);
            } else if (args[curArg].equals("-bucket")) {
                bucket = readArg(args);
            } else if (args[curArg].equals("-records")) {
                recordCount = Integer.parseInt(readArg(args));
            } else if (args[curArg].equals("-operations")) {
                operationCount = Integer.parseInt(readArg(args));
            } else if (args[curArg].equals("-threads")) {
                threadCount = Integer.parseInt(readArg(args));
            } else if (args[curArg].equals("-insertstart")) {
                insertStart = Integer.parseInt(readArg(args));
            } else if (args[curArg].equals("-optype")) {
                String op = readArg(args);
                try {
                    operationType = OperationType.valueOf(OperationType.class, op.toUpperCase());
                } catch (IllegalArgumentException e) {
                    usageMessage();
                    System.exit(0);
                }
            } else if (args[curArg].equals("-persistto")) {
                String per = readArg(args);
                try {
                    persistTo = PersistTo.valueOf(PersistTo.class, per.toUpperCase());
                } catch (IllegalArgumentException e) {
                    usageMessage();
                    System.exit(0);
                }
            } else if (args[curArg].equals("-replicateto")) {
                String rep = readArg(args);
                try {
                    replicateTo = ReplicateTo.valueOf(ReplicateTo.class, rep.toUpperCase());
                } catch (IllegalArgumentException e) {
                    usageMessage();
                    System.exit(0);
                }
            } else {
                System.out.println("Unknown option " + args[curArg]);
                usageMessage();
                System.exit(0);
            }

            if (curArg >= args.length) {
                break;
            }
        }

        if (curArg != args.length) {
            usageMessage();
            System.exit(0);
        }

        if (recordCount == 0 || threadCount == 0) {
            usageMessage();
            System.exit(0);
        }

        if (operationType != OperationType.INSERT && operationCount == 0) {
            usageMessage();
            System.exit(0);
        }

        runThreads();

        if (operationType == OperationType.READ) {
            System.out.println("PAUSE!");
            Thread.sleep(10000);
            System.out.println("SECOND WAVE!");
            runThreads();
        }
    }

    private static String readArg(String[] args) {
        curArg++;
        if (curArg >= args.length) {
            usageMessage();
            System.exit(0);
        }
        String value = args[curArg];
        curArg++;
        return value;
    }

    private static void runThreads() throws InterruptedException {
        ClientThread[] threads = new ClientThread[threadCount];
        long start = insertStart;
        long recordsPerThread = recordCount / threadCount;
        for (int i = 0; i < threadCount; i++) {
            long end = start + recordsPerThread;
            threads[i] = new ClientThread(new CouchbaseClient(host, port, bucket, user, password, persistTo, replicateTo),
                    operationCount, start, end, operationType);
            start = end;
        }
        for (int i = 0; i < threadCount; i++) {
            threads[i].start();
        }
        for (int i = 0; i < threadCount; i++) {
            threads[i].join();
        }
    }
}

