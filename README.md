# Cybersecurity Labs

A set of practical Python exercises covering core application security concepts: password strength evaluation, classical and modern cryptography, key derivation, digital signatures, steganography, and SQL injection.

## Labs

| # | Topic | Key concepts | Stack |
|---|-------|--------------|-------|
| [lab01](./lab01) | Password Strength Analyzer | Scoring a password's strength (1–10) based on length, character variety, and reuse of personal data | Python, `re` |
| [lab02](./lab02) | Classical Cipher Comparison | Caesar vs. Vigenère ciphers, key predictability, letter-uniqueness as a frequency-analysis resistance metric | Python |
| [lab03](./lab03) | LSB Steganography | Hiding a text message inside a PNG image using least-significant-bit encoding; bit/byte-level impact analysis | Python, Pillow |
| [lab04](./lab04) | Simplified Digital Signature | SHA-256 hashing, XOR-based signing as a simplified stand-in for asymmetric encryption, tamper detection | Python |
| [lab05](./lab05) | Symmetric Email Encryption | AES-256-GCM authenticated encryption, PBKDF2HMAC key derivation (100k+ iterations), per-message salt, Base64 key sharing | Python, `cryptography` |
| [lab06](./lab06) | SQL Injection: Vulnerable vs. Secure | Side-by-side comparison of a query built via string concatenation (exploitable via `' OR 1=1 --`) and the same query using parameterized statements (`?` placeholders) | Python, SQLite |

## Running the labs

Each lab is self-contained and runs as a standalone console script. See the README inside each lab folder for exact setup and run instructions.

General requirements: Python 3.x, plus per-lab dependencies (`Pillow` for lab03, `cryptography` for lab05) installed via `pip install <package>`.

## Note

Completed as part of a university cybersecurity course.
