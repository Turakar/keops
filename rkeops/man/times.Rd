% Generated by roxygen2: do not edit by hand
% Please edit documentation in R/lazytensor_operations.R
\name{*}
\alias{*}
\title{Multiplication.}
\usage{
x * y
}
\arguments{
\item{x}{A \code{LazyTensor}, a \code{ComplexLazyTensor}, a vector of numeric values,
or a scalar value.}

\item{y}{A \code{LazyTensor}, a \code{ComplexLazyTensor}, a vector of numeric values,
or a scalar value.}
}
\value{
An object of class "LazyTensor" if the function is called with a
\code{LazyTensor}, and an object of class "numeric", otherwise.
}
\description{
Symbolic binary operation for multiplication.
}
\details{
If \code{x} or \code{y} is a \code{LazyTensor}, \code{x * y} returns a \code{LazyTensor}
that encodes, symbolically, the element-wise product of \code{x} and \code{y}.
(In case one of the arguments is a vector or a scalar, it is first converted
to \code{LazyTensor}). If none of the arguments is a \code{LazyTensor}, it is equivalent
to the "*" R operator.

\strong{Note}

\code{x} and \code{y} input arguments should have the same inner dimension or be of
dimension 1.
}
\examples{
\dontrun{
x <- matrix(runif(150 * 3), 150, 3) # arbitrary R matrix, 150 rows and 3 columns
y <- matrix(runif(250 * 3), 250, 3) # arbitrary R matrix, 250 rows and 3 columns
x_i <- LazyTensor(x, index = 'i')   # creating LazyTensor from matrix x, 
                                    # indexed by 'i'
y_j <- LazyTensor(y, index = 'j')   # creating LazyTensor from matrix y, 
                                    # indexed by 'j'
                                    
x_times_y <- x_i * y_j              # symbolic matrix
}
}
\author{
Chloe Serre-Combe, Amelie Vernay
}
