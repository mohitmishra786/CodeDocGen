/**
 * Calculates the sum of two numeric values.
 * @returns The sum of a and b.
 */
function sum(a, b) { return a + b; }
/**
 * Calculates the difference between two values.
 * @returns The difference between a and b.
 */
function diff(a, b) { return a - b; }
/**
 * Increments a given value by 1.
 * @param {number} x - The value to increment.
 * @returns {number} The incremented value.
 */
const inc = (x) => x + 1;
/**
 * Calculates the decrement of a given value.
 * @param {number} x The value to decrement.
 * @returns {number} The decremented value.
 */
const dec = x => x - 1;
/**
 * Multiplies two numbers.
 * @returns The product of a and b.
 */
const multiply = function(a, b) { return a * b; };
/**
 * Clamps a value within a specified range.
 * @param {any} x - The value to be clamped.
 * @param {any} min - The minimum value of the range.
 * @param {any} max - The maximum value of the range.
 * @returns {any} The clamped value.
 */
class Utils { clamp(x, min, max) { if (x < min) return min; if (x > max) return max; return x; } isEven(n) { return n % 2 === 0; } }
