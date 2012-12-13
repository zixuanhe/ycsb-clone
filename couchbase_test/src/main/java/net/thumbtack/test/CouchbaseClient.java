package net.thumbtack.test;

import com.couchbase.client.CouchbaseConnectionFactory;
import com.couchbase.client.CouchbaseConnectionFactoryBuilder;
import net.spy.memcached.FailureMode;
import net.spy.memcached.compat.log.Logger;
import net.spy.memcached.compat.log.LoggerFactory;
import net.spy.memcached.internal.GetFuture;
import net.spy.memcached.internal.OperationFuture;

import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.*;

import static java.util.concurrent.TimeUnit.MILLISECONDS;

public class CouchbaseClient {

    protected final Logger log = LoggerFactory.getLogger(getClass());

    private static final int READ_BUFFER_SIZE = 16384;
    private static final long OP_TIMEOUT = 1000;
    private static final long SHUTDOWN_TIMEOUT = 1000;
    private static final FailureMode FAILURE_MODE = FailureMode.Redistribute;

    private static final int OK = 1;
    private static final int ERROR = 0;

    private com.couchbase.client.CouchbaseClient client;

    private String host;
    private int port;
    private String bucket;
    private String user;
    private String password;

    public CouchbaseClient(String host, int port, String bucket, String user, String password) {
        this.host = host;
        this.port = port;
        this.bucket = bucket;
        this.user = user;
        this.password = password;
    }

    public void init() throws IOException, URISyntaxException {
        CouchbaseConnectionFactoryBuilder builder = new CouchbaseConnectionFactoryBuilder();
        builder.setReadBufferSize(READ_BUFFER_SIZE);
        builder.setOpTimeout(OP_TIMEOUT);
        builder.setFailureMode(FAILURE_MODE);

        List<URI> servers = new ArrayList<URI>();
        servers.add(new URI("http://" + host + ":" + port + "/pools"));
        CouchbaseConnectionFactory connectionFactory = builder.buildCouchbaseConnection(servers, bucket, user, password);
        client = new com.couchbase.client.CouchbaseClient(connectionFactory);
    }

    public void cleanup() {
        if (client != null) {
            client.shutdown(SHUTDOWN_TIMEOUT, MILLISECONDS);
        }
    }

    public int read(String key) {
        try {
            GetFuture<Object> future = client.asyncGet(key);
            String document = (String) future.get();
            if (document == null) {
                return ERROR;
            }
            return OK;
        } catch (Exception e) {
            log.error("Error encountered", e);
            return ERROR;
        }
    }

    public int insert(String key, String value) {
        try {
            OperationFuture<Boolean> future = client.add(key, Integer.MAX_VALUE, value);
            return getReturnCode(future);
        } catch (Exception e) {
            log.error("Error inserting value", e);
            return ERROR;
        }
    }

    protected int getReturnCode(OperationFuture<Boolean> future) {
        if (future.getStatus().isSuccess()) {
            return OK;
        }
        log.error("Error inserting value %s : %s", future.getStatus().getMessage(), future.getKey());
        return ERROR;
    }

}
