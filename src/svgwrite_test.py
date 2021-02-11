import svgwrite

# set units to mm 
dwg = svgwrite.Drawing('test.svg', profile='tiny', size=('170mm', '130mm'), viewBox=('0 0 170 130'))
dwg.add(dwg.line((0, 0), (100, 100), stroke=svgwrite.rgb(255, 255, 16))).dasharray([10,1])
dwg.add(dwg.line((100, 0), (-100, 100), stroke='blue', stroke_width=1)).dasharray([10,1])
dwg.add(dwg.text('Test', insert=(10, 50), fill='red'))
#dwg.add(dwg.rect((0,0), (500, 200), fill="none"))
dwg.save()
