package org.sharkdetector.flink.function;

import jdk.vm.ci.meta.Value;
import org.apache.flink.api.common.state.BroadcastState;
import org.apache.flink.api.common.state.MapStateDescriptor;
import org.apache.flink.api.common.state.ValueState;
import org.apache.flink.api.common.state.ValueStateDescriptor;
import org.apache.flink.api.common.typeinfo.Types;
import org.apache.flink.configuration.Configuration;
import org.apache.flink.streaming.api.functions.co.KeyedBroadcastProcessFunction;
import org.apache.flink.util.Collector;
import org.sharkdetector.flink.util.Alert;
import org.sharkdetector.flink.util.QuoteMovement;
import org.sharkdetector.flink.util.Threshold;

import java.util.Map;
//TODO: processBroadcastElement
public class UpdatableQuoteMovementAlertFunction extends KeyedBroadcastProcessFunction<String, QuoteMovement, Map<String,Threshold>, Alert> {
    private MapStateDescriptor<String,Threshold> bcStateDescriptor = new MapStateDescriptor<>("thresholds", Types.STRING,Types.POJO(Threshold.class));
    private ValueState<Integer> lastSellVolChange, lastBuyVolChange;
    private ValueState<Float> lastSellQueuePrice, lastBuyQueuePrice;
    private ValueState<Integer> lastSellAlertCount, lastBuyAlertCount;
    @Override
    public void open(Configuration parameters) throws Exception {
        lastSellVolChange = getRuntimeContext().getState(new ValueStateDescriptor<>("lastSellVolChange",Types.INT));
        lastBuyVolChange = getRuntimeContext().getState(new ValueStateDescriptor<>("lastSellVolChange",Types.INT));
        lastSellQueuePrice = getRuntimeContext().getState(new ValueStateDescriptor<>("lastSellQueuePrice",Types.FLOAT));
        lastBuyQueuePrice = getRuntimeContext().getState(new ValueStateDescriptor<>("lastBuyQueuePrice",Types.FLOAT));
        lastSellAlertCount = getRuntimeContext().getState(new ValueStateDescriptor<>("lastSellAlertCount",Types.INT));
        lastBuyAlertCount = getRuntimeContext().getState(new ValueStateDescriptor<>("lastBuyAlertCount",Types.INT));
        super.open(parameters);
    }

    @Override
    public void processElement(QuoteMovement quoteMovement, ReadOnlyContext readOnlyContext, Collector<Alert> out) throws Exception {
        Threshold threshold = readOnlyContext
                .getBroadcastState(bcStateDescriptor)
                .get(quoteMovement.getCodeName());
        if(quoteMovement.getQueueType() == "Sell"){
            if(quoteMovement.getQueueVolumeChange() > threshold.sellThreshold){
                lastSellAlertCount.update(lastSellAlertCount.value() + 1);
                out.collect(new Alert(quoteMovement.getCodeName(), quoteMovement.getTimestamp(), quoteMovement.getQueueVolume(), quoteMovement.getQueueVolumeChange(), quoteMovement.getQueuePrice(), quoteMovement.getQueueType()));
            }
            lastSellVolChange.update(quoteMovement.getQueueVolumeChange());
            lastSellQueuePrice.update(quoteMovement.getQueuePrice());
        }else if(quoteMovement.getQueueType() == "Buy"){
            if(quoteMovement.getQueueVolumeChange() > threshold.buyThreshold){
                lastBuyAlertCount.update(lastBuyAlertCount.value() + 1);
                out.collect(new Alert(quoteMovement.getCodeName(), quoteMovement.getTimestamp(), quoteMovement.getQueueVolume(), quoteMovement.getQueueVolumeChange(), quoteMovement.getQueuePrice(), quoteMovement.getQueueType()));
            }
            lastBuyVolChange.update(quoteMovement.getQueueVolumeChange());
            lastBuyQueuePrice.update(quoteMovement.getQueuePrice());
        }
    }

    @Override
    public void processBroadcastElement(Map<String, Threshold> stringThresholdMap, Context context, Collector<Alert> collector) throws Exception {
        BroadcastState<String,Threshold> bcThresholdStates = context.getBroadcastState(bcStateDescriptor);
        for(String key: stringThresholdMap.keySet()){
            bcThresholdStates.put(key,stringThresholdMap.get(key));
        }
    }

}
