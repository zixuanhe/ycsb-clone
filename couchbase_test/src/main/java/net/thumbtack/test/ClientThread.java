package net.thumbtack.test;

import java.util.Random;

class ClientThread extends Thread {

    private final CouchbaseClient client;
    private final long operationCount;
    private final long insertStart;
    private final long insertEnd;
    private final Func func;

    interface Func {
        void run();
    }

    public ClientThread(CouchbaseClient _client, long _operationCount, long _insertStart, long _insertEnd, boolean isRead) {
        this.client = _client;
        this.operationCount = _operationCount;
        this.insertStart = _insertStart;
        this.insertEnd = _insertEnd;
        if(isRead) {
            func = new Func() {
                @Override
                public void run() {
                    Random randomKey = new Random();
                    for (int i = 0; i < operationCount; i++) {
                        client.read(String.valueOf((int) (randomKey.nextDouble() * (insertEnd - insertStart) + insertStart)));
                    }
                }
            };
        } else {
            func = new Func() {
                @Override
                public void run() {
                    RandomString randomString = new RandomString(1000);
                    for (long i = insertStart; i < insertEnd; i++) {
                        client.insert(String.valueOf(i), randomString.nextString());
                    }
                }
            };
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