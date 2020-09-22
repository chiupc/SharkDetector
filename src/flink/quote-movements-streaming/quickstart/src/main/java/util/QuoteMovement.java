package util;

public class QuoteMovement {
    public Long timestamp;
    public String code;
    public Integer lastDoneVol;
    public Float lastDonePrice;
    public String lastDoneType;
    public Integer buyQueueVol;
    public Integer sellQueueVol;
    public Integer buyQueueVolChg;
    public Integer sellQueueVolChg;
    public Float buyQueuePrice;
    public Float sellQueuePrice;

    /**
     * Empty default constructor to satify Flink's POJO requirements.
     */
    public QuoteMovement() { }

    public QuoteMovement(String code, Integer lastDoneVol, Float lastDonePrice, String lastDoneType, Integer buyQueueVol, Integer sellQueueVol, Integer buyQueueVolChg, Integer sellQueueVolChg, Float buyQueuePrice, Float sellQueuePrice, Long timestamp) {
        this.code = code;
        this.lastDoneVol = lastDoneVol;
        this.lastDonePrice = lastDonePrice;
        this.lastDoneType = lastDoneType;
        this.buyQueueVol = buyQueueVol;
        this.sellQueueVol = sellQueueVol;
        this.buyQueueVolChg = buyQueueVolChg;
        this.sellQueueVolChg = sellQueueVolChg;
        this.buyQueuePrice = buyQueuePrice;
        this.sellQueuePrice = sellQueuePrice;
        this.timestamp = timestamp;
    }

    @Override
    public String toString() {
        return "QuoteMovement{" +
                "code='" + code + '\'' +
                ", lastDoneVol=" + lastDoneVol +
                ", lastDonePrice=" + lastDonePrice +
                ", lastDoneType='" + lastDoneType + '\'' +
                ", buyQueueVol=" + buyQueueVol +
                ", sellQueueVol=" + sellQueueVol +
                ", buyQueueVolChg=" + buyQueueVolChg +
                ", sellQueueVolChg=" + sellQueueVolChg +
                ", buyQueuePrice=" + buyQueuePrice +
                ", sellQueuePrice=" + sellQueuePrice +
                '}';
    }
}
