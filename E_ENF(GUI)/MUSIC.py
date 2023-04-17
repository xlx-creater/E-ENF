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


def pseudospectrum_MUSIC(x, L, M=None, Fe=1, f=None):
    r""" This function compute the MUSIC pseudospectrum. The pseudo spectrum is defined as

        .. math:: S(f)=\frac{1}{\|\textbf{G}^{H}\textbf{a}(f) \|}

        where :math:`\textbf{G}` corresponds to the noise subspace and :math:`\textbf{a}(f)` is the steering vector. The peek locations give the frequencies of the signal.

        :param x: ndarray of size N
        :param L: int. Number of components to be extracted.
        :param M:  int, optional. Size of signal block.
        :param Fe: float. Sampling Frequency.
        :param f: nd array. Frequency locations f where the pseudo spectrum is evaluated.
        :returns: ndarray
        """

    # length of the vector x
    N = x.shape[0]

    if np.any(f) == None:
        f = np.linspace(0., Fe // 2, 512)

    if M == None:
        M = N // 2

    # extract noise subspace
    R = compute_autocovariance(x, M)
    U, S, V = lg.svd(R)
    G = U[:, L:]

    # compute MUSIC pseudo spectrum
    N_f = f.shape
    cost = np.zeros(N_f)

    for indice, f_temp in enumerate(f):
        # construct a (note that there a minus sign since Yn are defined as [y(n), y(n-1),y(n-2),..].T)
        vect_exp = -2j * np.pi * f_temp * np.arange(0, M) / Fe
        a = np.exp(vect_exp)
        a = np.transpose(np.matrix(a))
        # Cost function
        cost[indice] = 1. / lg.norm((G.H) * a)

    return f, cost


def root_MUSIC(x, L, M, Fe):
    r""" This function estimate the frequency components based on the roots MUSIC algorithm [BAR83]_ . The roots Music algorithm find the roots of the following polynomial

        .. math:: P(z)=\textbf{a}^{H}(z)\textbf{G}\textbf{G}^{H}\textbf{a}(z)

        The frequencies are related to the roots as

        .. math:: z=e^{-2j\pi f/Fe}

        :param x: ndarray of size N
        :param L: int. Number of components to be extracted.
        :param M:  int, optional. Size of signal block.
        :param Fe: float. Sampling Frequency.
        :returns: ndarray containing the L frequencies

        """

    # length of the vector x
    N = x.shape[0]

    if M == None:
        M = N // 2

    # extract noise subspace
    R = compute_autocovariance(x, M)
    U, S, V = lg.svd(R)
    G = U[:, L:]

    # construct matrix P
    P = G * G.H

    # construct polynomial Q
    Q = 0j * np.zeros(2 * M - 1)
    # Extract the sum in each diagonal
    for (idx, val) in enumerate(range(M - 1, -M, -1)):
        diag = np.diag(P, val)
        Q[idx] = np.sum(diag)

    # Compute the roots
    roots = np.roots(Q)

    # Keep the roots with radii <1 and with non zero imaginary part
    roots = np.extract(np.abs(roots) < 1, roots)
    roots = np.extract(np.imag(roots) != 0, roots)

    # Find the L roots closest to the unit circle
    distance_from_circle = np.abs(np.abs(roots) - 1)
    index_sort = np.argsort(distance_from_circle)
    component_roots = roots[index_sort[:L]]

    # extract frequencies ((note that there a minus sign since Yn are defined as [y(n), y(n-1),y(n-2),..].T))
    angle = abs(-np.angle(component_roots))

    # frequency normalisation
    f = float(Fe * angle / (2. * np.pi))

    return f

def MUSIC (Signal,Window,StepPoints,Fs):
   FrameSize       = Window
   Signal2         = np.zeros((Signal.shape[0],int(FrameSize/2)*2 + Signal.shape[1]))
   Signal2[:, int(FrameSize/2):int(FrameSize/2)+Signal.shape[1]] = Signal
   WindowPositions = range(1, Signal2.shape[1] - int(FrameSize)+2, StepPoints)
   # WindowPositions = range(0, Signal.shape[1], StepPoints)
   IF0             = np.zeros(len(WindowPositions))

   for i in range(len(WindowPositions)):
       IF0[i] = root_MUSIC(Signal2[:,WindowPositions[i]:WindowPositions[i] + int(FrameSize)], 1, None, Fs)
       # IF0[i] = root_MUSIC(Signal[:, WindowPositions[i]:WindowPositions[i] + int(FrameSize)], 1, None, Fs)
   return IF0
