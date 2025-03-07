% Generated by roxygen2: do not edit by hand
% Please edit documentation in R/lazytensor_operations.R
\name{concat}
\alias{concat}
\title{Concatenation.}
\usage{
concat(x, y)
}
\arguments{
\item{x}{A \code{LazyTensor} or a \code{ComplexLazyTensor}.}
}
\value{
A \code{LazyTensor} or a \code{ComplexLazyTensor} that encodes, symbolically,
the concatenation of \code{x} and \code{y} along their inner dimension.
}
\description{
Concatenation of two \code{LazyTensor} or \code{ComplexLazyTensor}. A binary operation.
}
\details{
If \code{x} and \code{y} are two \code{LazyTensor} or \code{ComplexLazyTensor},
\code{concat(x, y)} encodes, symbolically, the concatenation of \code{x} and \code{y} along
their inner dimension. TODO check if this is, indeed, along the inner dimension !
}
\examples{
\dontrun{
x <- matrix(runif(150 * 3), 150, 3) # arbitrary R matrix, 150 rows, 3 columns
y <- matrix(runif(250 * 3), 250, 3) # arbitrary R matrix, 250 rows, 3 columns
x_i <- LazyTensor(x, index = 'i')   # LazyTensor from matrix x, indexed by 'i'
y_j <- LazyTensor(y, index = 'j')   # LazyTensor from matrix x, indexed by 'j'                                     

concat_xy <- concat(x_i, y_j)
}
}
\author{
Chloe Serre-Combe, Amelie Vernay
}
