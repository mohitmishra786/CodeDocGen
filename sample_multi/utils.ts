/**
 * Greets a person by name.
 * @param name The name of the person to greet.
 * @returns A string greeting the person by name.
 */
function greet(name: string): string { return `Hello, ${name}!`; }
/**
 * Calculates the result of adding two numbers or returns the first number if the second is undefined.
 * @param x - The first number.
 * @param y - The second number (optional).
 * @returns The result of the calculation or the first number if y is undefined.
 */
class A { public calc(x: number, y?: number): number { return y ? x + y : x; } protected doIt<T>(val: T): T { return val; } }
/**
 * Doubles a given number.
 * @param {number} n - The number to be doubled.
 * @returns {number} The doubled number.
 */
const twice = (n: number): number => n*2;