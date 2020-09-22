package org.sharkdetector.quotemovements_streaming;

import com.sun.org.slf4j.internal.Logger;
import org.apache.flink.api.java.utils.ParameterTool;
import org.apache.flink.streaming.api.functions.source.SourceFunction;
import util.QuoteMovement;

//import org.apache.logging.log4j.Logger;
//import org.apache.logging.log4j.LogManager;

public class QuoteMovementMonitoring {
    //private static final Logger logger = LogManager.getLogger(QuoteMovementMonitoring.class);
    public static void main(String[] args) throws Exception {
        final SourceFunction<QuoteMovement> source;
        final ParameterTool params = ParameterTool.fromArgs(args);

        if(params.has("kafka-topic")){
            String kafkaTopic = params.get("kafka-topic");
            String brokers = params.get("brokers");
            //logger.in
        }
    }
}
