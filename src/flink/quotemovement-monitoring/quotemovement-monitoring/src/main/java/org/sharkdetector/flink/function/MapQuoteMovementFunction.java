package org.sharkdetector.flink.function;

import org.apache.flink.api.common.functions.MapFunction;
import org.sharkdetector.flink.util.QuoteMovement;
import org.sharkdetector.flink.util.QuoteMovementRaw;

public class MapQuoteMovementFunction implements MapFunction<QuoteMovementRaw, QuoteMovement> {

    @Override
    public QuoteMovement map(QuoteMovementRaw quoteMovementRaw) throws Exception {
        String queueType;
        String codeName = quoteMovementRaw.CodeName();
        Long timestamp = Long.valueOf(quoteMovementRaw.Time());
        Integer queueVolume;
        Integer queueVolumeChange;
        Float queuePrice;
        if(quoteMovementRaw.Buy_Queue_Vol != "" && quoteMovementRaw.Buy_Queue_Price != ""){
            queueType = "Buy";
            queueVolume = Integer.valueOf(quoteMovementRaw.Buy_Queue_Vol);
            queuePrice = Float.valueOf(quoteMovementRaw.Buy_Queue_Price);
            queueVolumeChange = Integer.valueOf(quoteMovementRaw.Buy_Queue_Vol_Change);
            return new QuoteMovement(codeName, timestamp, queueVolume, queueVolumeChange, queuePrice, queueType);
        }else if(quoteMovementRaw.Sell_Queue_Vol != "" && quoteMovementRaw.Sell_Queue_Price != ""){
            queueType = "Sell";
            queueVolume = Integer.valueOf(quoteMovementRaw.Sell_Queue_Vol);
            queuePrice = Float.valueOf(quoteMovementRaw.Sell_Queue_Price);
            queueVolumeChange = Integer.valueOf(quoteMovementRaw.Sell_Queue_Vol_Change);
            return new QuoteMovement(codeName, timestamp, queueVolume, queueVolumeChange, queuePrice, queueType);
        }else if(quoteMovementRaw.Last_Done_Vol != "" && quoteMovementRaw.Last_Done_Price != ""){
            if(quoteMovementRaw.Type == "Buy Up"){
                queueType = "Last Done Buy Up";
            }else if(quoteMovementRaw.Type == "Sell Down"){
                queueType = "Last Done Sell Down";
            }else{
                queueType = "Last Done Unknown";
            }
            queueVolume = Integer.valueOf(quoteMovementRaw.Last_Done_Vol);
            queuePrice = Float.valueOf(quoteMovementRaw.Last_Done_Price);
            queueVolumeChange = 0;
            return new QuoteMovement(codeName, timestamp, queueVolume, queueVolumeChange, queuePrice, queueType);
        }

        return null;
    }
}
