def levenshteinDistance(s1, s2):
    m, n = len(s1), len(s2)
    
    # Initialize a (m+1) x (n+1) matrix
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    # Base cases: Transforming an empty string to another
    for i in range(m + 1):
        dp[i][0] = i  # Cost of deleting characters
    for j in range(n + 1):
        dp[0][j] = j  # Cost of inserting characters
    
    # Fill the matrix
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                cost = 0
            else:
                cost = 1
            
            dp[i][j] = min(
                dp[i - 1][j] + 1,    # Deletion
                dp[i][j - 1] + 1,    # Insertion
                dp[i - 1][j - 1] + cost  # Substitution
            )
    
    return dp[m][n]