package org.sharkdetector.flink.util;

import java.util.Map;

public class Threshold {
    public Float buyThreshold;
    public Float sellThreshold;

    public Threshold(Float buyThreshold, Float sellThreshold) {
        this.buyThreshold = buyThreshold;
        this.sellThreshold = sellThreshold;
    }

    @Override
    public String toString() {
        return "Threshold{" +
                ", buyThreshold=" + buyThreshold +
                ", sellThreshold=" + sellThreshold +
                '}';
    }
}
