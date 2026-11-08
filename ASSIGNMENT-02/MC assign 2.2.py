import numpy as np

def allocate_subcarriers(U, K, R_min, rate_matrix):
    """
    Allocates subcarriers to users based on minimum rate requirements 
    and maximum sum-rate greedy strategy.
    
    Parameters:
    - U: Number of users
    - K: Number of subcarriers
    - R_min: Minimum rate required for each user
    - rate_matrix: A 2D numpy array of shape (U, K) representing achievable rates
    """
    # Initialize variables
    # Keep track of unallocated subcarriers using indices
    free_subcarriers = list(range(K))
    tot = np.zeros(U)                      # Total rates achieved per user
    allocation = {u: [] for u in range(U)} # Tracks which subcarrier goes to which user

    # --- Phase 1: Satisfy Needy Users ---
    # Loop runs while any user is below R_min AND there are still free subcarriers
    while np.any(tot < R_min) and len(free_subcarriers) > 0:
        # Find 'needy users' who haven't met their R_min yet
        needy_users = np.where(tot < R_min)[0]
        
        # u = argmin(tot[needy users]) -> Find the most deprived user among the needy
        u = needy_users[np.argmin(tot[needy_users])]
        
        # k = argmax(rate[u, free]) -> Find the best available subcarrier for this user
        # 1. Get the rates of free subcarriers for user 'u'
        free_rates = rate_matrix[u, free_subcarriers]
        # 2. Find the index of the highest rate inside that subset
        best_free_idx = np.argmax(free_rates)
        # 3. Map it back to the actual subcarrier ID
        k = free_subcarriers[best_free_idx]
        
        # Assign k to u; tot[u] += rate[u,k]
        allocation[u].append(k)
        tot[u] += rate_matrix[u, k]
        
        # Remove the allocated subcarrier from the free pool
        free_subcarriers.remove(k)

    # --- Phase 2: Max-Sum for Remaining Free Subcarriers ---
    # Allocate whatever is left to whoever gets the highest rate out of it
    for k in list(free_subcarriers): # Iterate over a copy of remaining free ones
        # assign k to argmax_u rate[u,k]
        best_user = np.argmax(rate_matrix[:, k])
        
        allocation[best_user].append(k)
        tot[best_user] += rate_matrix[best_user, k]
        free_subcarriers.remove(k)

    return allocation, tot


# ==========================================
# --- Example Execution Scenario ---
# ==========================================

# 1. Define configuration constants
NUM_USERS = 3
NUM_SUBCARRIERS = 8
MIN_RATE_REQUIRED = 15.0  # R_min for each user

# 2. Generate a random rate matrix (U x K) representing channel qualities
# Seed set for reproducible results
np.random.seed(42)
# Rates randomly generated between 2.0 and 10.0 units
achievable_rates = np.random.uniform(2.0, 10.0, size=(NUM_USERS, NUM_SUBCARRIERS))

print("--- Achievable Rate Matrix (Rows=Users, Cols=Subcarriers) ---")
print(np.round(achievable_rates, 2))
print(f"\nTarget Minimum Rate (R_min) per user: {MIN_RATE_REQUIRED}\n")

# 3. Run the algorithm
subcarrier_mapping, total_user_rates = allocate_subcarriers(
    U=NUM_USERS, 
    K=NUM_SUBCARRIERS, 
    R_min=MIN_RATE_REQUIRED, 
    rate_matrix=achievable_rates
)

# 4. Print results out cleanly
print("--- Final Allocation Results ---")
for user_id in range(NUM_USERS):
    print(f"User {user_id}:")
    print(f"  Assigned Subcarriers: {subcarrier_mapping[user_id]}")
    print(f"  Total Rate Achieved:  {total_user_rates[user_id]:.2f} (Target met: {total_user_rates[user_id] >= MIN_RATE_REQUIRED})")
