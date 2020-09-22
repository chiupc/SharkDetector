package org.sharkdetector.flink.schema;

import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.module.SimpleModule;
import org.apache.flink.streaming.connectors.kafka.KafkaDeserializationSchema;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.sharkdetector.flink.util.Threshold;

import javax.annotation.Nullable;
import java.util.HashMap;
import java.util.Map;

public class ThresholdDeserializer implements KafkaDeserializationSchema<Map<String,Threshold>> {

    private static ObjectMapper objectMapper = new ObjectMapper()
            .registerModule(new SimpleModule());

    @Override
    public boolean isEndOfStream(Map<String, Threshold> threshold) {
        return false;
    }
    //TODO: Add quote movement deserialization from kafka record. Need to consider null value
    @Nullable
    @Override
    public Map<String, Threshold> deserialize(ConsumerRecord<byte[], byte[]> consumerRecord) throws Exception {
        Threshold threshold = objectMapper.readValue(consumerRecord.value(), Threshold.class);
        Map<String, Threshold> thresholds = new HashMap<>();
        thresholds.put(consumerRecord.key().toString(),threshold);
        return thresholds;
    }

    @Override
    public TypeInformation<Map<String, Threshold>> getProducedType() {
        return null;
    }
}
