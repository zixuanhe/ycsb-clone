package net.thumbtack.test;

import java.util.Random;

class ClientThread extends Thread {

    private final static int VALUE_LENGTH = 1000;

    private final CouchbaseClient client;
    private final long operationCount;
    private final long insertStart;
    private final long insertEnd;
    private final Func func;

    interface Func {
        void run();
    }

    public ClientThread(CouchbaseClient _client, long _operationCount, long _insertStart, long _insertEnd, OperationType operationType) {
        this.client = _client;
        this.operationCount = _operationCount;
        this.insertStart = _insertStart;
        this.insertEnd = _insertEnd;
        switch (operationType) {
            case INSERT: {
                func = new Func() {
                    public void run() {
                        RandomString randomString = new RandomString(VALUE_LENGTH);
                        for (long i = insertStart; i < insertEnd; i++) {
                            client.insert(String.valueOf(i), randomString.nextString());
                        }
                    }
                };
                break;
            }
            case READ: {
                func = new Func() {
                    public void run() {
                        Random randomKey = new Random();
                        for (int i = 0; i < operationCount; i++) {
                            client.read(String.valueOf((int) (randomKey.nextDouble() * (insertEnd - insertStart) + insertStart)));
                        }
                    }
                };
                break;
            }
            case UPDATE: {
                func = new Func() {
                    public void run() {
                        Random randomKey = new Random();
                        RandomString randomString = new RandomString(VALUE_LENGTH);
                        for (int i = 0; i < operationCount; i++) {
                            client.update(String.valueOf((int) (randomKey.nextDouble() * (insertEnd - insertStart) + insertStart)), randomString.nextString());
                        }
                    }
                };
                break;
            }
            default: {
                throw new UnsupportedOperationException(operationType.toString());
            }
        }
    }

    @Override
    public void run() {
        try {
            client.init();
        } catch (Exception e) {
            e.printStackTrace();
        }
        func.run();
        client.cleanup();
    }
}