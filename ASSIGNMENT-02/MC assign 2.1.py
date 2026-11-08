import numpy as np
from scipy.linalg import hadamard

def walsh(L):
    """Generates a Hadamard/Walsh matrix of size L."""
    return hadamard(L)

def random_pm1(rows, cols):
    """Generates a matrix of random +1 and -1 values."""
    return np.random.choice([-1, 1], size=(rows, cols))

def ber1(L, K, kind, ebn0, n, strong=None, power=10, async_=False):
    # 1. Generate spreading codes (C)
    if kind == "walsh":
        C = walsh(L)[1:K+1]  # Shape: (K, L)
    else:
        C = random_pm1(K, L) # Shape: (K, L)
        
    # 2. Handle Near-Far effect (amplitudes)
    amp = np.ones(K)
    if strong is not None:
        amp[strong] = np.sqrt(power) 
        
    # 3. Generate random data bits (+1 / -1)
    b = random_pm1(K, n) # Shape: (K, n)
    
    # 4. Transmit signal (Modulation & Spreading)
    # Shape of tx: (K, n * L)
    tx = (b[:, :, None] * C[:, None, :]).reshape(K, -1) * amp[:, None]
    
    # 5. Handle Asynchronous offsets
    if async_:
        for k in range(K):
            random_offset = np.random.randint(0, L)
            tx[k] = np.roll(tx[k], random_offset)
            
    # 6. Add AWGN Noise based on Eb/N0
    # Eb/N0 in linear scale
    ebn0_linear = 10 ** (ebn0 / 10.0)
    
    # Energy per bit for User 0 (assuming base amp=1, Eb = L)
    Eb = L 
    N0 = Eb / ebn0_linear
    sigma = np.sqrt(N0 / 2) # Noise standard deviation
    
    # Combine signals and add channel noise matching rx shape
    rx = tx.sum(axis=0) + sigma * np.random.randn(n * L)
    
    # 7. Receiver - Despreading specifically for User 0
    # Reshape back to (n, L) and matrix-multiply by User 0's code vector C[0]
    z = rx.reshape(n, L) @ C[0] # Shape: (n,)
    
    # 8. Calculate Bit Error Rate (BER) for User 0
    errors = np.sum((z > 0) != (b[0] > 0))
    ber = errors / n
    
    return ber

# --- Example Testing ---
# Using a low Eb/N0 (like 0dB or 2dB) ensures you see active bit errors!
bit_error_rate = ber1(L=64, K=8, kind="random", ebn0=2, n=10000, strong=None, power=10, async_=False)
print(f"Bit Error Rate (BER): {bit_error_rate}")
