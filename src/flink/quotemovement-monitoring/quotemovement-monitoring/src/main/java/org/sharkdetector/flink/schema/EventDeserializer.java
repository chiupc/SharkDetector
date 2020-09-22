package org.sharkdetector.flink.schema;

import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.module.SimpleModule;
import org.apache.flink.streaming.connectors.kafka.KafkaDeserializationSchema;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.sharkdetector.flink.util.QuoteMovementRaw;

public class EventDeserializer implements KafkaDeserializationSchema<QuoteMovementRaw> {

    private static ObjectMapper objectMapper = new ObjectMapper()
            .registerModule(new SimpleModule());

    @Override
    public boolean isEndOfStream(QuoteMovementRaw quoteMovementRaw) {
        return false;
    }

    @Override
    public QuoteMovementRaw deserialize(ConsumerRecord<byte[], byte[]> consumerRecord) throws Exception {
        QuoteMovementRaw quoteMovementRaw = objectMapper.readValue(consumerRecord.value(), QuoteMovementRaw.class);
        quoteMovementRaw.setCodeName(consumerRecord.key().toString());
        return quoteMovementRaw;
    }

    @Override
    public TypeInformation<QuoteMovementRaw> getProducedType() {
        return TypeInformation.of(QuoteMovementRaw.class);
    }

}
