double angle(float x1,float x2,float y1,float y2) {
  if(x2 == 0 && y2 == 0) return 1;
  double vector=x1*x2+y1*y2,dis=dist(0,0,x1,y1)*dist(0,0,x2,y2);
  return vector/dis;
}
boolean clockwise(PVector p1,PVector p2,PVector p3) {//true:clockwise,pop;false:nopop
  float x1=p1.x,x2=p2.x,x3=p3.x;
  float y1=p1.y,y2=p2.y,y3=p3.y;
  float result=(x2-x1)*(y3-y1)-(y2-y1)*(x3-x1);
  if(result > 0) return false;
  else return true;
}
void convexhull() {
  int base=0;
  double[] po=new double[n-1];
  for(int i=1;i<n;i++) {
    if(point[i].y < point[base].y || (point[i].y == point[base].y && point[i].x < point[base].x)) {
      base=i;
    }
  }
  if(base != n-1) {
    PVector temp=point[base];
    point[base]=point[n-1];
    point[n-1]=temp;
  }
  for(int i=0;i<n-1;i++) {
    po[i]=angle(5,point[i].x-point[n-1].x,0,point[i].y-point[n-1].y);
  }
  for(int i=0;i<n-1;i++) {
    for(int j=0;j<n-i-2;j++) {
      if(po[j] < po[j+1]) {
        double tmp=po[j];
        po[j]=po[j+1];
        po[j+1]=tmp;
        PVector temp=point[j];
        point[j]=point[j+1];
        point[j+1]=temp;
      }
    }
  }
  hull.add(point[n-1]);
  hull.add(point[0]);
  hull.add(point[1]);
  for(int i=2;i<n-1;i++) {
    while(true) {
      boolean state=clockwise(hull.get(hull.size()-2),hull.get(hull.size()-1),point[i]);
      if(state) hull.remove(hull.size()-1);
      else {
        hull.add(point[i]);
        break;
      }
    }
  }
}