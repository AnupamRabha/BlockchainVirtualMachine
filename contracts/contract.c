#include <stdint.h>
int foo;
int bar;
void calc() {
    bar = 150;
    if (bar > 100) {
        foo = 10 * 20;
    } else {
        foo = 10 * 10;
    }
}