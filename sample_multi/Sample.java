public class Sample {
    /**
     * Computes the sum of two integers.
     * @param a The first integer.
     * @param b The second integer.
     * @return The sum of a and b.
     */
    public int add(int a, int b) { return a + b; }
    /**
     * Computes the difference between two integers.
     * @param a The first integer.
     * @param b The second integer.
     * @return The result of subtracting b from a.
     */
    public int sub(int a, int b) { return a - b; }
    /**
     * @brief Multiplies two integers.
     * @param a The first integer to multiply.
     * @param b The second integer to multiply.
     * @return The product of a and b.
     */
    public int mul(int a, int b) { return a * b; }
    /**
     * Computes the division of two double values, ensuring that the result is accurate and handles potential division by zero errors.
     * The function takes two double parameters, a and b, and returns their division result.
     */
    public double div(double a, double b) { if (b == 0) throw new IllegalArgumentException("b must not be 0"); return a / b; }
    /**
     * @brief Returns a personalized greeting message for the specified individual.
     * @param name The name of the person to be greeted.
     * @return A string greeting message.
     */
    public static String greet(String name) { return "Hello, " + name; }
    /**
     * @brief Concatenates two strings into a single string.
     * @param a The first string to be joined.
     * @param b The second string to be joined.
     * @return The resulting concatenated string.
     */
    public String join(String a, String b) { return a + b; }
    /**
     * Computes the maximum value between two integers.
     * @param a The first integer.
     * @param b The second integer.
     * @return The maximum value of a and b.
     */
    public int max(int a, int b) { return a > b ? a : b; }
    /**
     * Computes the sum of all elements in the given integer array.
     * Returns the total sum of all elements in the array.
     */
    public static int sumAll(int[] nums) { int s = 0; for (int n : nums) s += n; return s; }
}
