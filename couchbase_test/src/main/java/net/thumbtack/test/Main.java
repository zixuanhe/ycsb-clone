package net.thumbtack.test;

import java.io.FileInputStream;
import java.io.IOException;
import java.net.URISyntaxException;
import java.util.Enumeration;
import java.util.Properties;

public class Main {

    private static int curArg = 0;

    private static String host = "127.";
    private static int port = 8091;
    private static String bucket = "default";
    private static String user = "";
    private static String password = "";

    private static long recordCount = 0;
    private static long operationCount = 0;
    private static int threadCount = 0;
    private static long insertStart = 0;
    private static boolean doInserts = true;

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
        System.out.println("  -operations n: number of read operations (required for '-optype read' only)");
        System.out.println("  -threads n: number of threads");
        System.out.println("  -optype [insert|read]: specified type of operations");
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
                if (op.equals("insert")) {
                    doInserts = true;
                } else if (op.equals("read")) {
                    doInserts = false;
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

        if (!doInserts && operationCount == 0) {
            usageMessage();
            System.exit(0);
        }

        runThreads();

        if (!doInserts) {
            System.out.println("PAUSE FOR 10 SECONDS!");
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
            threads[i] = new ClientThread(new CouchbaseClient(host, port, bucket, user, password),
                    operationCount, start, end, !doInserts);
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

