# Fungsi untuk menghitung penjumlahan aritmatika menggunakan rumus
def sum_arithmetic_formula(a, d, n):
    return (n * (2 * a + (n - 1) * d)) // 2

def main():
    # Input dari user
    a = int(input("Masukkan suku pertama (a): "))
    d = int(input("Masukkan selisih antar suku (d): "))
    n = int(input("Masukkan jumlah suku (n): "))

    # Hitung menggunakan rumus matematis
    result_formula = sum_arithmetic_formula(a, d, n)
    print(f"Hasil penjumlahan aritmatika menggunakan rumus: {result_formula}")

    # Hitung menggunakan metode iteratif
    result_iterative = sum_arithmetic_iterative(a, d, n)
    print(f"Hasil penjumlahan aritmatika secara iteratif: {result_iterative}")

if __name__ == "__main__":
    main()
