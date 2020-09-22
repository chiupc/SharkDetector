package org.sharkdetector.flink.util;

/**
 * Data type for quote movement alerts
 */
public class QuoteMovement {

    private String codeName;
    private Long timestamp;
    private Integer queueVolume;
    private Integer queueVolumeChange;
    private Float queuePrice;
    private String queueType;

    public QuoteMovement(){

    }

    /**
     * @param codeName: Code
     * @param timestamp: Event timestamp
     * @param queueVolume: Volume of queue order
     * @param queueVolumeChange: Volume change of queue order
     * @param queuePrice: Price of queue order
     * @param queueType: Type of queue order
     */

    public QuoteMovement(String codeName, Long timestamp, Integer queueVolume, Integer queueVolumeChange, Float queuePrice, String queueType) {
        this.codeName = codeName;
        this.timestamp = timestamp;
        this.queueVolume = queueVolume;
        this.queueVolumeChange = queueVolumeChange;
        this.queuePrice = queuePrice;
        this.queueType = queueType;
    }

    public String getCodeName() {
        return codeName;
    }

    public Long getTimestamp() {
        return timestamp;
    }

    public String getQueueType() {
        return queueType;
    }

    public Integer getQueueVolume() {
        return queueVolume;
    }

    public Integer getQueueVolumeChange() {
        return queueVolumeChange;
    }

    public Float getQueuePrice() {
        return queuePrice;
    }

    @Override
    public String toString() {
        return "Alert{" +
                "codeName='" + codeName + '\'' +
                ", timestamp=" + timestamp +
                ", queueVolume=" + queueVolume +
                ", queuePrice=" + queuePrice +
                ", queueType='" + queueType + '\'' +
                '}';
    }
}
