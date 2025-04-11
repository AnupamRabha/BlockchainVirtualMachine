#include <stdint.h>
int foo;
int bar;
void calc() {
    foo = 100 - 30;
    bar = foo;
    foo = 20 + 10;
}