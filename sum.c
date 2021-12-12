// sum.c use ggc sum.c -o sum to get a sample executable file for debugging using GDB
#include <stdio.h> 

int sum (int a, int b) { 
	int c; 
	c = a + b; 
	return c; 
} 

int main() { 
	int x, y, z; 
	printf("\nEnter the first number: "); 
	scanf("%d", &x); 
	printf("Enter the second number: "); 
	scanf("%d", &y); 
	z = sum (x, y); 
	printf("The sum is %d\n\n", z); 
	return 0; 
}
