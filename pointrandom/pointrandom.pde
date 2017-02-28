int n=100,margin=40;
PVector[] point=new PVector[n];
ArrayList<PVector> hull=new ArrayList<PVector>(); //<>// //<>// //<>//
void setup() {
  size(640,480);
  background(0);
  for(int i=0;i<n;i++) {
    point[i]=new PVector(random(width-margin),random(height-margin));
    if(point[i].x < margin) point[i].x+=margin;
    if(point[i].y < margin) point[i].y+=margin;
  }
  smooth();
  noLoop();
  convexhull(); //<>//
}
void draw() {
  int hullsize=hull.size();
  stroke(255);
  strokeWeight(5);
  for(int i=0;i<n;i++) {
    point(point[i].x,point[i].y);
  }
  strokeWeight(1);
  for(int i=0;i<hullsize;i++) {
    if(i != hullsize-1) line(hull.get(i).x,hull.get(i).y,hull.get(i+1).x,hull.get(i+1).y);
    else line(hull.get(hullsize-1).x,hull.get(hullsize-1).y,hull.get(0).x,hull.get(0).y);
  }
}