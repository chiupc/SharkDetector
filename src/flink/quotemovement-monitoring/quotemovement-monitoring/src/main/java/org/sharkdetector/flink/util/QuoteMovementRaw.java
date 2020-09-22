package org.sharkdetector.flink.util;

public class QuoteMovementRaw {
    public String Time;
    public String CodeName;
    public String Last_Done_Vol;
    public String Last_Done_Price;
    public String Type;
    public String Buy_Queue_Vol;
    public String Sell_Queue_Vol;
    public String Buy_Queue_Vol_Change;
    public String Sell_Queue_Vol_Change;
    public String Buy_Queue_Price;
    public String Sell_Queue_Price;

    /**
     * Empty default constructor to satify Flink's POJO requirements.
     */
    public QuoteMovementRaw() { }

    public QuoteMovementRaw(String time, String codeName, String last_Done_Vol, String last_Done_Price, String type, String buy_Queue_Vol, String sell_Queue_Vol, String buy_Queue_Vol_Change, String sell_Queue_Vol_Change, String buy_Queue_Price, String sell_Queue_Price) {
        this.Time = time;
        this.CodeName = codeName;
        this.Last_Done_Vol = last_Done_Vol;
        this.Last_Done_Price = last_Done_Price;
        this.Type = type;
        this.Buy_Queue_Vol = buy_Queue_Vol;
        this.Sell_Queue_Vol = sell_Queue_Vol;
        this.Buy_Queue_Vol_Change = buy_Queue_Vol_Change;
        this.Sell_Queue_Vol_Change = sell_Queue_Vol_Change;
        this.Buy_Queue_Price = buy_Queue_Price;
        this.Sell_Queue_Price = sell_Queue_Price;
    }

    @Override
    public String toString() {
        return "QuoteMovement{" +
                "Time=" + Time +
                ", CodeName='" + CodeName + '\'' +
                ", Last_Done_Vol=" + Last_Done_Vol +
                ", Last_Done_Price=" + Last_Done_Price +
                ", Type='" + Type + '\'' +
                ", Buy_Queue_Vol=" + Buy_Queue_Vol +
                ", Sell_Queue_Vol=" + Sell_Queue_Vol +
                ", Buy_Queue_Vol_Change=" + Buy_Queue_Vol_Change +
                ", Sell_Queue_Vol_Change=" + Sell_Queue_Vol_Change +
                ", Buy_Queue_Price=" + Buy_Queue_Price +
                ", Sell_Queue_Price=" + Sell_Queue_Price +
                '}';
    }

    public String CodeName() {
        return this.CodeName;
    }

    public String Time() {
        return Time;
    }

    public void setCodeName(String codeName) {
        this.CodeName = codeName;
    }
}
