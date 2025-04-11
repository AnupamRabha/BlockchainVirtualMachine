
public class Contract {
    public int foo;
    public int bar;
    public void calc() {
        foo = 100 - 30;
        bar = foo;
        foo = 20 + 10;
    }
}