package org.sharkdetector.flink;

import org.apache.flink.api.common.serialization.SimpleStringSchema;
import org.apache.flink.api.common.state.MapStateDescriptor;
import org.apache.flink.api.common.typeinfo.Types;
import org.apache.flink.api.java.utils.ParameterTool;
import org.apache.flink.contrib.streaming.state.RocksDBStateBackend;
import org.apache.flink.runtime.state.filesystem.FsStateBackend;
import org.apache.flink.streaming.api.datastream.BroadcastStream;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.datastream.DataStreamSink;
import org.apache.flink.streaming.api.datastream.KeyedStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.functions.source.SourceFunction;
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaConsumer;
import org.apache.flink.streaming.connectors.rabbitmq.RMQSink;
import org.apache.flink.streaming.connectors.rabbitmq.common.RMQConnectionConfig;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.sharkdetector.flink.function.MapQuoteMovementFunction;
import org.sharkdetector.flink.function.UpdatableQuoteMovementAlertFunction;
import org.sharkdetector.flink.schema.EventDeserializer;
import org.sharkdetector.flink.schema.ThresholdDeserializer;
import org.sharkdetector.flink.util.QuoteMovement;
import org.sharkdetector.flink.util.QuoteMovementRaw;
import org.sharkdetector.flink.util.Threshold;

import java.util.Map;
import java.util.Properties;

public class QuoteMovementMonitoring {
    private static final Logger logger = LogManager.getLogger(QuoteMovementMonitoring.class);
    public static void main(String[] args) throws Exception {
        final SourceFunction<QuoteMovementRaw> source;
        final SourceFunction<Map<String,Threshold>> thresholds;
        final ParameterTool params = ParameterTool.fromArgs(args);
        String rabbitMQHost = params.get("rabbitmq-host");
        Integer rabbitMQPort = params.getInt("rabbitmq-port");
        final RMQConnectionConfig connectionConfig = new RMQConnectionConfig.Builder()
                .setHost(rabbitMQHost)
                .setPort(rabbitMQPort)
                .build();

        if(params.has("quote_tasks_kafka_topic") && params.has("quote_thresholds_kafka_topic")){
            String quoteMovementTopic = params.get("quote_tasks_kafka_topic");
            String quoteThresholdsTopic = params.get("quote_thresholds_kafka_topic");
            String brokers = params.get("brokers");
            logger.info("Getting quote movements from kafka brokers...");

            Properties kafkaProps = new Properties();
            kafkaProps.setProperty("bootstrap.servers",brokers);

            FlinkKafkaConsumer<QuoteMovementRaw> quoteMovementsKafka = new FlinkKafkaConsumer<>(quoteMovementTopic, new EventDeserializer(), kafkaProps);
            FlinkKafkaConsumer<Map<String,Threshold>> quoteThresholdsKafka = new FlinkKafkaConsumer<>(quoteThresholdsTopic, new ThresholdDeserializer(), kafkaProps);
            quoteMovementsKafka.setStartFromLatest();
            quoteMovementsKafka.setCommitOffsetsOnCheckpoints(false);
            source = quoteMovementsKafka;
            thresholds = quoteThresholdsKafka;
        }else{
            throw new Exception("Kafka configuration is not found. Please run with the required arguments.");
        }
        // create the stream execution environment and configure the execution
        final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        env.enableCheckpointing(5000L);
        // initialize state backend persistent storage. default to memory if filesystem or rocksDB is not specified.
        final String stateBackend = params.get("backend", "memory");
        if("files".equals(stateBackend)){
            final String checkpointDir = params.get("checkpoint-dir");
            //if async is used, states will be first copied to local storage and asynchronously copied to remote storage in async mode
            boolean asyncCheckPoints = params.getBoolean("async-checkpoints",false);
            env.setStateBackend(new FsStateBackend(checkpointDir));
        } else if("rocks".equals(stateBackend)){
            final String checkpointDir = params.get("checkpoint-dir");
            boolean incrementalCheckPoints = params.getBoolean("incremental-checkpoints", false);
            env.setStateBackend(new RocksDBStateBackend(checkpointDir,incrementalCheckPoints));
        }
        // make parameters available in the web interface
        env.getConfig().setGlobalJobParameters(params);

        //create data stream from quote movements data source
        DataStream<QuoteMovementRaw> quoteMovements = env.addSource(source);

        KeyedStream keyedQuoteMovements = quoteMovements.keyBy(QuoteMovementRaw::CodeName);

        //prepare broadcast states descriptor
        MapStateDescriptor<String,Threshold> bcStateDescriptor = new MapStateDescriptor<>("thresholds", Types.STRING,Types.POJO(Threshold.class));
        DataStream<Map<String,Threshold>> thresholdsDataStream = env.addSource(thresholds);
        BroadcastStream bcedThresholds = thresholdsDataStream.broadcast(bcStateDescriptor);
        KeyedStream<QuoteMovement, String> quoteMovementDataStream =  quoteMovements
                .map(new MapQuoteMovementFunction())
                .keyBy(QuoteMovement::getCodeName);
        DataStream<String> alerts = quoteMovementDataStream
                .connect(bcedThresholds)
                .process(new UpdatableQuoteMovementAlertFunction());

        DataStreamSink<String> rabbitSink = alerts
                .addSink(new RMQSink<>(
                    connectionConfig,            // config for the RabbitMQ connection
                    "alert-queue",                 // name of the RabbitMQ queue to send messages to
                    new SimpleStringSchema()));// serialization schema to turn Java objects to messages

        env.execute("Quote Movements Threshold Detection");
    }

}

