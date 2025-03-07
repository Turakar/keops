% Generated by roxygen2: do not edit by hand
% Please edit documentation in R/lazytensor_preprocess.R
\name{is.ComplexLazyParameter}
\alias{is.ComplexLazyParameter}
\title{is.ComplexLazyParameter?}
\usage{
is.ComplexLazyParameter(x)
}
\arguments{
\item{x}{A \code{LazyTensor} object that we want to know if
it is a \code{ComplexLazyParameter}.}
}
\value{
A boolean, TRUE or FALSE.
}
\description{
Checks whether if the given input is a \code{ComplexLazyTensor} encoding
a single complex value. That is, if the input is a fixed parameter
\code{ComplexLazyTensor} of dimension 1.
}
\details{
If \code{x} is a fixed parameter \code{ComplexLazyTensor} encoding a
single complex value, \code{is.ComplexLazyParameter(x)}
returns TRUE, else, returns FALSE.
}
\examples{
\dontrun{
# basic example
scal <- 3.14
cplx <- 2 + 3i
v <- rep(3 + 7i, 10)
z <- matrix(2 + 1i^ (-6:5), nrow = 4)

# create LazyTensor and ComplexLazyTensor
scal_LT <- LazyTensor(scal)
cplx_LT <- LazyTensor(cplx)
v_LT <- LazyTensor(v)
z_i <- LazyTensor(z, index = 'i')

# call is.ComplexLazyParameter
is.ComplexLazyParameter(scal_LT) # returns FALSE
is.ComplexLazyParameter(cplx_LT) # returns TRUE
is.ComplexLazyParameter(v_LT) # returns FALSE
is.ComplexLazyParameter(x_i) # returns FALSE
}
}
\author{
Chloe Serre-Combe, Amelie Vernay
}
