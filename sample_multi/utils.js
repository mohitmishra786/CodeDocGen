/**
 * Calculates the sum of two numbers.
 * @returns The sum of a and b.
 */
function sum(a, b) { return a + b; }
/**
 * Calculates the difference between two values.
 * @param a The first value.
 * @param b The second value.
 * @returns The difference between a and b.
 */
function diff(a, b) { return a - b; }
/**
 * Increments a given value by 1.
 * @param x The value to increment.
 * @returns The incremented value.
 */
const inc = (x) => x + 1;
/**
 * Calculates the decrement of a given value.
 * @param {number} x - The value to decrement.
 * @returns {number} The decremented value.
 */
const dec = x => x - 1;
/**
 * Multiplies two numbers together.
 * @param a any - The first number to multiply.
 * @param b any - The second number to multiply.
 * @returns The product of a and b.
 */
const multiply = function(a, b) { return a * b; };
/**
 * Clamps a value within a specified range.
 * @param x The value to be clamped.
 * @param min The minimum value of the range (inclusive).
 * @param max The maximum value of the range (inclusive).
 * @returns The clamped value, which is either the input value if it is within the range, or the nearest boundary value if it is outside.
 */
class Utils { clamp(x, min, max) { if (x < min) return min; if (x > max) return max; return x; } isEven(n) { return n % 2 === 0; } }
