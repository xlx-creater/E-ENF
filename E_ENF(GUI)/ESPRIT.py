import numpy as np
from numpy import linalg as lg

def compute_autocovariance(x, M):
    r""" This function compute the auto-covariance matrix of a numpy signal. The auto-covariance is computed as follows

        .. math:: \textbf{R}=\frac{1}{N}\sum_{M-1}^{N-1}\textbf{x}_{m}\textbf{x}_{m}^{H}

        where :math:`\textbf{x}_{m}^{T}=[x[m],x[m-1],x[m-M+1]]`.

        :param x: ndarray of size N
        :param M:  int, optional. Size of signal block.
        :returns: ndarray

        """

    # Create covariance matrix for psd estimation
    # length of the vector x
    N = x.shape[0]

    # Create column vector from row array
    x_vect = np.transpose(np.matrix(x))

    # init covariance matrix
    yn = x_vect[M - 1::-1]
    R = yn * yn.H
    for indice in range(1, N - M):
        # extract the column vector
        yn = x_vect[M - 1 + indice:indice - 1:-1]
        R = R + yn * yn.H

    R = R / N
    return R

def Esprit(x, L, M, Fe):
    r""" This function estimate the frequency components based on the ESPRIT algorithm [ROY89]_

        The frequencies are related to the roots as :math:`z=e^{-2j\pi f/Fe}`. See [STO97]_ section 4.7 for more information about the implementation.

        :param x: ndarray of size N
        :param L: int. Number of components to be extracted.
        :param M:  int, optional. Size of signal block.
        :param Fe: float. Sampling Frequency.
        :returns: ndarray ndarray containing the L frequencies

        """

    L = L + 1
    x = np.asarray(x).squeeze()
    assert x.ndim in (1, 2)
    # length of the vector x
    if x.ndim == 1:
        N = x.size
    else:
        N = x.shape[1]

    if M is None:
        M = N // 2
    # %% extract signal subspace  99.9 % of computation time

    if x.ndim == 1 and isinstance(M, int):
        R = compute_autocovariance(x, M)  # 75% of computation time
    else:
        # the random phase of transmit/receive/target actually helps--need at least 5-6 observations to make useful
        R = np.cov(x, rowvar=False)

    # R = subspace.corrmtx(x.astype(complex128),M).astype(float) #f2py fortran

    U, S, V = lg.svd(R)  # 25% of computation time
    # %% take eigenvalues and determine sinusoid frequencies
    # Remove last row
    S1 = U[:-1, :L]
    # Remove first row
    S2 = U[1:, :L]

    # Compute matrix Phi (Stoica 4.7.12)  <0.1 % of computation time
    Phi = lg.inv(S1.conj().T @ S1) @ S1.conj().T @ S2

    # Perform eigenvalue decomposition <0.1 % of computation time
    V, U = lg.eig(Phi)

    # extract frequencies ((note that there a minus sign since Yn are defined as [y(n), y(n-1),y(n-2),..].T))
    ang = abs(-np.angle(V))

    # frequency normalisation
    f = Fe * ang / (2.0 * np.pi)

    return f[0]

def ESPRIT (Signal,Window,StepPoints,Fs):
   FrameSize       = Window
   Signal2         = np.zeros(int(FrameSize/2)*2 + len(Signal))
   Signal2[int(FrameSize/2):int(FrameSize/2)+len(Signal)] = Signal
   WindowPositions = range(1, len(Signal2) - int(FrameSize)+2, StepPoints)
   IF0             = np.zeros(len(WindowPositions))

   for i in range(len(WindowPositions)):
       IF0[i] = Esprit(Signal2[WindowPositions[i]:WindowPositions[i] + int(FrameSize)], 1, None, Fs)
   return IF0