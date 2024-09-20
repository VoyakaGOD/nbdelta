class EditorialAction:
    MATCH = 'M'
    INSERT = 'I'
    DELETE = 'D'

def get_editorial_matrix(old, new) -> list[list[int]]:
    M = len(old) + 1
    N = len(new) + 1
    D = [[0 for n in range(N)] for m in range(M)]
    for j in range(1, N):
        D[0][j] = j
    for i in range(1, M):
        D[i][0] = i
    for i in range(1, M):
        for j in range(1, N):
            if old[i - 1] == new[j - 1]:
                D[i][j] = D[i - 1][j - 1]
            else:
                D[i][j] = min(D[i - 1][j], D[i][j - 1]) + 1
    return D

def get_editorial_prescription(old, new) -> tuple[list[EditorialAction], int, int]:
    D = get_editorial_matrix(old, new)
    i = len(old)
    j = len(new)
    result = []
    inserts = 0
    deletions = 0
    while (i > 0) or (j > 0):
        if (i > 0) and (j > 0) and (D[i - 1][j - 1] == D[i][j]) and (old[i - 1] == new[j - 1]):
            result = [EditorialAction.MATCH] + result
            i -= 1
            j -= 1
        elif (i > 0) and (D[i - 1][j] + 1 == D[i][j]):
            result = [EditorialAction.DELETE] + result
            deletions += 1
            i -= 1
        else:
            result = [EditorialAction.INSERT] + result
            inserts += 1
            j -= 1
    return result, inserts, deletions
