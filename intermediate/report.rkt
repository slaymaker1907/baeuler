#lang scribble/base
@(require scribble-math)

@title{Music Theory Analysis Using Topology Progress Report}
@author{Dyllon Gagnier}

@section{Project Description}

I intend to apply and adapt existing topological techniques in order to provide an abstract representation of sheet music. From an initial review of exising methods,
while using topology to analyze music has been done before, these works seem to be focusing more on classical topology rather than the computational methods we talked about in class.
Additionally, the focus of this project is less on producing a tool for music theorists but instead creating a graphical representation that allows musicians to quickly get some idea about the structure
of a given piece. If possible, it would also be ideal if this representation was simple and intuitive enough to explain the harmony of common practice era (Western classical music) pieces to non-musicians.

@subsection{Expanded Data Analysis Process}

The following is the high level topological process that will be performed that was apparently a little vague in the proposal.

@(itemlist #:style 'numbered
           @item{Load and parse scores from music21 using MusicXML.}
           @item{Run the score through a chordification process in music21.}
           @item{Convert each note to a 2d point using the Tonnetz representation centered on C.}
           @item{Condense triads of points in the Tonnetz representation to a single center point in 2d.}
           @item{Run the mapper algorithm over these points using the bottleneck distance (since there are sets of triads/2d points) and time as the mapper function.}
           @item{Annotate original score with the topological information gained from mapper.}
           )

Note that while the one-hot vector could potentially be run through mapper directly, the Tonnetz representation seems interesting to look at since it gives a distance measurement which
is both a metric as well as being meaningful from a music theoretic standpoint.

Chordification is a transformation of the sheet music which inserts a chord for each distinguishable point in the original score. A point in time of the score is distinguishable if there
is a new note beginning or ending at that particular point in time. Therefore, it makes it easier to analyze which notes are playing at any given point in the piece.

@section{Completed Milestones/Preliminiary Results}

@(itemlist
  @item{I have set up a Django python server on my local machine.}
  @item{I have set up a basic React front end}
  @item{I have set up the music and topological libararies needed from python (mainly music21 and scikit-tda)}
  @item{The front end can display both the original score as well as "choridified" version of any input MusicXML file (currently using the large corpus in music21).}
  @item{Better formalized topological process for transforming the scores.}
  )

The initial effort so far has been very much focused on setting up the plumbing to support the final analysis and application.
The progress is more thoroughly summarized in the above list, but I have been successful in setting up all of the libraries I should need (particularly music21 and scikit-tda which provides the
abstract representation of scores and an implementation of mapper respectively).

@section{Upcoming Milestones}

@(itemlist
  @item{Implement the topological analysis component as an API on the server.}
  @item{Display this analysis in conjunction with the full and chordified scores.}
  @item{Deploy server and frontend on a public facing server.}
  @item{Publish code publically on GitHub.})

@section{Summary}

Overall, I am slightly behind schedule since project setup with the frontend and server took a bit longer than anticipated, but I should be able to get on track within the next couple of days. The main
outstanding milestone that is not currently complete is actually implementing the topological pipeline on the server. However, the analysis I am currently displaying on the frontend (the chordification) is
a bit more sophisticated than I anticipated being able to do before the progress report. I should not have trouble in completing the other milestones and having a fully functional topology based visualization
for music theory.
