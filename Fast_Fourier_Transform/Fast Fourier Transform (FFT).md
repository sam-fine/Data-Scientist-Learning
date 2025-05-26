---
attachments: [Clipboard_2023-06-21-11-05-01.png, Clipboard_2023-06-21-11-05-06.png]
tags: [Machine Learning Algorithms]
title: Fast Fourier Transform (FFT)
created: '2023-06-14T08:03:27.958Z'
modified: '2023-06-28T10:23:30.390Z'
---

# Fast Fourier Transform (FFT)

* General idea is we can take an arbitrary function f(x), defined on e.g. $2L$ periodic domains (as seen in the first jupyter notebook below) and approximate it with the infinite sum of sines and cosines of increasingly high frequency using Fourier Series.
* FFT is used to compute a fourier series efficienctly on a computer.
## Fourier Series
<center>$<f(x),g(x)> = \int_a^b f(x)\hat{g}(x)dx$</center> 
<> = inner product.

$\hat{g} =$ complex conjugate of g (as we are working in the complex plane)
So, we can represent our function like this:
<center>$f(x) = \frac{A_0}{2} + \displaystyle\sum_{k=1}^\infty (A_kcos(kx) + B_ksin(kx))$</center>

Where $A_k$ and $B_K$ are Fourier coefficients.

* Note: In practise, we do not sum up to infinity, so the Fourier series gives a great approximation when using a finite upper limit, e.g. k=10,20.
* The coefficients represent the projection of f onto the 'bases' directions. So $A_K$ represents the projection onto the cos(kx) direction, and $B_k$ represents the projection onto the sin(kx) direction. It informs us on the weights/ how much the function is in these directions.
* So, the sines and cosines are orthogonal functions, and we project the function f onto these directions/axis.
* The cosines and sines are $2\pi$ periodic.
Above is from: [https://www.youtube.com/watch?v=MB6XGQWLV04&list=PLMrJAkhIeNNT_Xh3Oy0Y4LTj0Oxo8GqsC&index=2]
## Complex Fourier Series
f(x) does not have to be real.
Say: 
<center>$f(x) = \displaystyle\sum_{k=-\infty}^\infty C_ke^{ikx}$</center>
With:
<center>$C_k = \frac{1}{2\pi}<f(x),\phi_k> = \frac{1}{2L}\int_{-L}^L f(x)e^\frac{ik\pi{x}}{L}dx$</center>
Remember Eulers' Equation:
<center>$e^{ikx} =cos(kx) + isin(kx) = \phi_k$</center>

For an example of a function being approximated by a Fourier Series in Python: go to: C:\Users\sfine\Documents\Notes\attachments\FFT_images\fourier_series_approx_eg.ipynb locally on Jupyter Notebook, 

This is from: [https://www.youtube.com/watch?v=dZrShAGqT44&list=PLMrJAkhIeNNT_Xh3Oy0Y4LTj0Oxo8GqsC&index=7]

## The Fourier Transform

Fourier Series is defined for periodic functions on domains, e.g. [-L,L]. 
The Fourier Transform is on an infinite domain, and is not periodic:
![](C:\Users\sfine\Documents\Notes\attachments\FFT_images\series_vs_transform.png)
To go from Series to Transform, you just let L tend to infinity.
To see this, view: 
[https://www.youtube.com/watch?v=jVYs-GTqm5Ulist=PLMrJAkhIeNNT_Xh3Oy0Y4LTj0Oxo8GqsC&index=10]
End with the result:
![](C:\Users\sfine\Documents\Notes\attachments\FFT_images\equations.png)
<center>$w_k =\frac{k\pi}{L} = frequency$</center>
One way to use these equations is to solve PDEs. You transform the PDE into Fourier space using the Fourier transform, differentiate and then transform the equation back using the inverse Fourier Transform.
It is easier to solve PDEs in the Fourier space.

## Discrete Fourier Transform (DFT) - For discrete data points
DFT - Mathematical transformation that can be written in terms of a matrix multiplication
FFT - computational efficient way of computing the DFT, that scales well to large data sets.

In many cases, we don't have an analytical function, but we have measurement data from an experiment:
![](C:\Users\sfine\Documents\Notes\attachments\FFT_images\DFT_intro.png)
So, we have some f defined at n discrete locations, $x_0,x_1...x_{n-1}$, a vector of data, $f_0,f_1...f_{n-1}$ (meant to be n-1 in pic)
We want to compute the discrete fourier series of this vector.

For each of the data points $f_k$, we want to find the fourier transform, $\hat{f}_k$ to find the vector of $\hat{f}$ that shows us the frequency components. This shows us how much of each frequency is in the data. $f_0$ is the lowest frequency and $f_{n-1}$ is the highest frequency.
We get:
<center>$\hat{f}_k = \displaystyle\sum_{j=0}^{n-1} f_je^\frac{-i2\pi{jk}}{n}$</center>
So the kth Fourier coefficient is calculated by taking the sum of all j data points at the kth frequency times the jth frequency divided by n.
Just like before, if we have our data ($f_1...f_n$) we can get a fourier transform, and via the inverse fourier transform, we can go back to our data:
<center>$f_k = (\displaystyle\sum_{j=0}^{n-1} \hat{f}_je^\frac{i2\pi{jk}}{n})\frac{1}{n}$</center>
Where $\frac{1}{n}$ is there for normalisation.
In the equations, we have a fudamental frequency ($w_n$) that is related to what kind of sines and cosines we can approximate to with n discrete values in a domain in x. The fourier transforms just add up integer multiples of that frequency, times by our data. 
<center>$w_n = e^\frac{-i2\pi}{n}$</center>
We will use $w_n$ to create a matrix that multiplies our data and gives us our fourier transform.
Just manually plug the k values into the equation and you get:

![](C:\Users\sfine\Documents\Notes\attachments\FFT_images\DFT_matrix.png)
Due to the fact we are working with discrete data points rather than continous fucntions, we can write the transformation in the form of a matrix.
Note, $w_n$ is a complex number so the DFT is a complex matrix, and the fourier coefficients ($f_k$) are complex values.
This means the magnitude of the $f_k$ values tell you how much of each mode/frequency (cosines and sines of that k) we have, and the angle of the value tells you what phase you have between the sine and cosine, so how much of each sine and cosine you have.
Note: creating the matrix is expensive, so we use the FFT

[https://www.youtube.com/watch?v=nl9TZanwbBk&list=PLMrJAkhIeNNT_Xh3Oy0Y4LTj0Oxo8GqsC&index=15]

The FFT is a lot faster than the DFT.
Scaling:
DFT = $O(n^2)$ (can see there are $n^2$ calculations when computing the n by n matrix)
FFT = $O(nlog(n))$ nearly linear for large n

## FFT
Assume the number of data points is a power of 2, e.g. $n=2^{10} =1024$, so the DFT matrix ($F_{1024}$) is a 1024 by 1024 matrix.
So: 
<center>$\hat{f} = F_{1024}f$</center>
The observation that makes the FFT possible is that if you re-organise f into its' even and odd coefficients, and stack them appropriately, $F_{1024}$ can be written in a much simpler format, consisting of identity matrices, diagonal matrices and a 512 by 512 matrix $F_{512}$:

![](C:\Users\sfine\Documents\Notes\attachments\FFT_images\simplified_DFT.png)
You get this by literally reorganising each row of the DFT matrix so the even and odd coefficients of f are stacked like above.
What is important is that the identity and diaganol matrices are very easy to compute, and the second combination of matrices consisting of $F_{512}$ is easier to compute than the $F_{1024}$ due to the large number of zeros.
Note: 

![](C:\Users\sfine\Documents\Notes\attachments\FFT_images\D_512_matrix.png)
Now we can go further, and split the $F_{512}$ matrix into smaller blocks by taking the even indices of the even indices of f, and the odd indices of the odd indices of f, and stack accordingly:

![](C:\Users\sfine\Documents\Notes\attachments\FFT_images\split_f_indices.png)
So we can keep splitting our F matrices into smaller and smaller matrices:
![](C:\Users\sfine\Documents\Notes\attachments\FFT_images\make_DFT_smaller.png)
So the FFT exploits symmetries in the DFT matrix to re-write the problem into a bunch of efficient matrix multiplications of smaller size, and if the number of data points is a power of 2, then you can keep re-writing the problem until you end up with a $F_2$ matrix.
**Note:** even if n is not a power of 2, it is still more efficient to pad out the DFT matrix with zeros until you do get a power of 2 matrix.
[https://www.youtube.com/watch?v=toj_IoCQE-4&list=PLMrJAkhIeNNT_Xh3Oy0Y4LTj0Oxo8GqsC&index=18]

## Use of FFT
* Derivatives, solving PDEs, Denoise data, data analysis
* Classic use of FFT is decomposing frequencies from sound (sound editing), but is used in many different areas of maths and physics.
![](C:\Users\sfine\Documents\Notes\attachments\FFT_images\superposition_waves.png)
* Here we see the superposition of four frequencies; D,A,F and C, with frequencies 294 and 440 respectively.
* The presure is the sum of each of these notes individually. At some points the peaks match up with each other and result in a high pressure, and others they cancel out.
* Result is a wave that is not a pure sine wave.
* The FFT separates the given wave into its composite frequencies, so it converts signals from the time domain to the frequency domain:
![](C:\Users\sfine\Documents\Notes\attachments\FFT_images\FFT_into_freqs.png)

A good visual explanation: [https://www.youtube.com/watch?v=spUNpyF58BY]

An example of denoising data with the FFT through python is located:
C:\Users\sfine\Documents\Learning Code\FFT_images\Denoising_data_using_FFT.ipynb
