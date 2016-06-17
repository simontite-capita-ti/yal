class Clp:
    program = """//CL//
    #define DIAG 0
    #define UP 1
    #define LEFT 2

    #define GAP -1

    __kernel void alignment_kernel(__global int * T, __global int * S_matrix,
            int t_N, int t_M, int d)
    {
      int col = get_global_id(1);
      int row = get_global_id(0);

      // Check if we are inside the table boundaries.
      if (!(row < t_N && col < t_M)) {
        return;
      }

     //  Check if current thread is on the current diagonal
      if (row + col != d) {
        return;
      }

      int v1;
      int v2;
      int v3;
      int v4;
      v1 = v2 = v3 = v4 = INT_MIN;

      if (row > 0 && col > 0) {
        v1 = T[t_M * (row - 1) + (col - 1)] + S_matrix[t_M * (row - 1) + (col - 1)];
      }
      if (row > 0 && col >= 0) {
        v2 = T[t_M * (row - 1) + col] + GAP;
      }
      if (row >= 0 && col > 0) {
        v3 = T[t_M * row + (col - 1)] + GAP;
      }
      if (row == 0 && col == 0) {
        v4 = 0;
      }

      T[ t_M * row + col ] = max( max(v1, v2), max(v3, v4));
    }
    """

