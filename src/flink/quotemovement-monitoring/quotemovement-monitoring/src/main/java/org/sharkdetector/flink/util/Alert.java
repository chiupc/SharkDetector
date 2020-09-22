package org.sharkdetector.flink.util;

/**
 * Create an Alert class to extend QuoteMovement for future extension
 */

public class Alert extends QuoteMovement {

    public Alert(String codeName, Long timestamp, Integer queueVolume, Integer queueVolumeChange, Float queuePrice, String queueType) {
        super(codeName, timestamp, queueVolume, queueVolumeChange, queuePrice, queueType);
    }

    @Override
    public String toString() {
        return super.toString();
    }
}
