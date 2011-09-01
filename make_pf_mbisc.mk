#
# python code for regenerating main code of this makefile:
# r=range(28,128)
# for i in r:
#    #print "${DATA_DIR}%d_traced_v0.svg\\" %i
#    print "${DATA_DIR}%d_traced_v0.svg: ${DATA_DIR}%d_pretrace_v1.svg" %(i,i)
#    print "\trm -f ${DATA_DIR}%d_traced_v0.svg" % i
#    print "\tpython parser_pax.py -p ${PARSER_NAME} -s %d -e %d -o ${DATA_DIR} -i ${DATA_DIR}"  %(i,i)
#    print "\tpython ${REGION_COMPARATOR} $@ ${DATA_DIR}%d_tracedclean_v0.svg" % i
#    print

PARSER_NAME = paxinos_franklin_mbisc
PARSERS_DIR = bin/parsers/${PARSER_NAME}/
ATLAS_DIR = atlases/${PARSER_NAME}/
DATA_DIR  = ${ATLAS_DIR}caf-src/
REGION_COMPARATOR = ${PARSERS_DIR}region_comparator.py

${DATA_DIR}index.xml: ${DATA_DIR}parents.txt ${DATA_DIR}fullnames.txt slides
	touch ${DATA_DIR}*_traced*v*.svg
	python parser_pax.py -p ${PARSER_NAME} -s 28 -e 127 --create-only-index-file  -o ${DATA_DIR} -i ${DATA_DIR}

all: slides ${DATA_DIR}index.xml
	echo "Done processing"

slides: ${DATA_DIR}28_traced_v0.svg ${DATA_DIR}29_traced_v0.svg\
	${DATA_DIR}30_traced_v0.svg ${DATA_DIR}31_traced_v0.svg\
	${DATA_DIR}32_traced_v0.svg ${DATA_DIR}33_traced_v0.svg\
	${DATA_DIR}34_traced_v0.svg ${DATA_DIR}35_traced_v0.svg\
	${DATA_DIR}36_traced_v0.svg ${DATA_DIR}37_traced_v0.svg\
	${DATA_DIR}38_traced_v0.svg ${DATA_DIR}39_traced_v0.svg\
	${DATA_DIR}40_traced_v0.svg ${DATA_DIR}41_traced_v0.svg\
	${DATA_DIR}42_traced_v0.svg ${DATA_DIR}43_traced_v0.svg\
	${DATA_DIR}44_traced_v0.svg ${DATA_DIR}45_traced_v0.svg\
	${DATA_DIR}46_traced_v0.svg ${DATA_DIR}47_traced_v0.svg\
	${DATA_DIR}48_traced_v0.svg ${DATA_DIR}49_traced_v0.svg\
	${DATA_DIR}50_traced_v0.svg ${DATA_DIR}51_traced_v0.svg\
	${DATA_DIR}52_traced_v0.svg ${DATA_DIR}53_traced_v0.svg\
	${DATA_DIR}54_traced_v0.svg ${DATA_DIR}55_traced_v0.svg\
	${DATA_DIR}56_traced_v0.svg ${DATA_DIR}57_traced_v0.svg\
	${DATA_DIR}58_traced_v0.svg ${DATA_DIR}59_traced_v0.svg\
	${DATA_DIR}60_traced_v0.svg ${DATA_DIR}61_traced_v0.svg\
	${DATA_DIR}62_traced_v0.svg ${DATA_DIR}63_traced_v0.svg\
	${DATA_DIR}64_traced_v0.svg ${DATA_DIR}65_traced_v0.svg\
	${DATA_DIR}66_traced_v0.svg ${DATA_DIR}67_traced_v0.svg\
	${DATA_DIR}68_traced_v0.svg ${DATA_DIR}69_traced_v0.svg\
	${DATA_DIR}70_traced_v0.svg ${DATA_DIR}71_traced_v0.svg\
	${DATA_DIR}72_traced_v0.svg ${DATA_DIR}73_traced_v0.svg\
	${DATA_DIR}74_traced_v0.svg ${DATA_DIR}75_traced_v0.svg\
	${DATA_DIR}76_traced_v0.svg ${DATA_DIR}77_traced_v0.svg\
	${DATA_DIR}78_traced_v0.svg ${DATA_DIR}79_traced_v0.svg\
	${DATA_DIR}80_traced_v0.svg ${DATA_DIR}81_traced_v0.svg\
	${DATA_DIR}82_traced_v0.svg ${DATA_DIR}83_traced_v0.svg\
	${DATA_DIR}84_traced_v0.svg ${DATA_DIR}85_traced_v0.svg\
	${DATA_DIR}86_traced_v0.svg ${DATA_DIR}87_traced_v0.svg\
	${DATA_DIR}88_traced_v0.svg ${DATA_DIR}89_traced_v0.svg\
	${DATA_DIR}90_traced_v0.svg ${DATA_DIR}91_traced_v0.svg\
	${DATA_DIR}92_traced_v0.svg ${DATA_DIR}93_traced_v0.svg\
	${DATA_DIR}94_traced_v0.svg ${DATA_DIR}95_traced_v0.svg\
	${DATA_DIR}96_traced_v0.svg ${DATA_DIR}97_traced_v0.svg\
	${DATA_DIR}98_traced_v0.svg ${DATA_DIR}99_traced_v0.svg\
	${DATA_DIR}100_traced_v0.svg ${DATA_DIR}101_traced_v0.svg\
	${DATA_DIR}102_traced_v0.svg ${DATA_DIR}103_traced_v0.svg\
	${DATA_DIR}104_traced_v0.svg ${DATA_DIR}105_traced_v0.svg\
	${DATA_DIR}106_traced_v0.svg ${DATA_DIR}107_traced_v0.svg\
	${DATA_DIR}108_traced_v0.svg ${DATA_DIR}109_traced_v0.svg\
	${DATA_DIR}110_traced_v0.svg ${DATA_DIR}111_traced_v0.svg\
	${DATA_DIR}112_traced_v0.svg ${DATA_DIR}113_traced_v0.svg\
	${DATA_DIR}114_traced_v0.svg ${DATA_DIR}115_traced_v0.svg\
	${DATA_DIR}116_traced_v0.svg ${DATA_DIR}117_traced_v0.svg\
	${DATA_DIR}118_traced_v0.svg ${DATA_DIR}119_traced_v0.svg\
	${DATA_DIR}120_traced_v0.svg ${DATA_DIR}121_traced_v0.svg\
	${DATA_DIR}122_traced_v0.svg ${DATA_DIR}123_traced_v0.svg\
	${DATA_DIR}124_traced_v0.svg ${DATA_DIR}125_traced_v0.svg\
	${DATA_DIR}126_traced_v0.svg ${DATA_DIR}127_traced_v0.svg

${DATA_DIR}28_traced_v0.svg: ${DATA_DIR}28_pretrace_v1.svg
	rm -f ${DATA_DIR}28_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 28 -e 28 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}28_tracedclean_v0.svg

${DATA_DIR}29_traced_v0.svg: ${DATA_DIR}29_pretrace_v1.svg
	rm -f ${DATA_DIR}29_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 29 -e 29 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}29_tracedclean_v0.svg

${DATA_DIR}30_traced_v0.svg: ${DATA_DIR}30_pretrace_v1.svg
	rm -f ${DATA_DIR}30_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 30 -e 30 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}30_tracedclean_v0.svg

${DATA_DIR}31_traced_v0.svg: ${DATA_DIR}31_pretrace_v1.svg
	rm -f ${DATA_DIR}31_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 31 -e 31 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}31_tracedclean_v0.svg

${DATA_DIR}32_traced_v0.svg: ${DATA_DIR}32_pretrace_v1.svg
	rm -f ${DATA_DIR}32_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 32 -e 32 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}32_tracedclean_v0.svg

${DATA_DIR}33_traced_v0.svg: ${DATA_DIR}33_pretrace_v1.svg
	rm -f ${DATA_DIR}33_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 33 -e 33 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}33_tracedclean_v0.svg

${DATA_DIR}34_traced_v0.svg: ${DATA_DIR}34_pretrace_v1.svg
	rm -f ${DATA_DIR}34_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 34 -e 34 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}34_tracedclean_v0.svg

${DATA_DIR}35_traced_v0.svg: ${DATA_DIR}35_pretrace_v1.svg
	rm -f ${DATA_DIR}35_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 35 -e 35 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}35_tracedclean_v0.svg

${DATA_DIR}36_traced_v0.svg: ${DATA_DIR}36_pretrace_v1.svg
	rm -f ${DATA_DIR}36_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 36 -e 36 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}36_tracedclean_v0.svg

${DATA_DIR}37_traced_v0.svg: ${DATA_DIR}37_pretrace_v1.svg
	rm -f ${DATA_DIR}37_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 37 -e 37 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}37_tracedclean_v0.svg

${DATA_DIR}38_traced_v0.svg: ${DATA_DIR}38_pretrace_v1.svg
	rm -f ${DATA_DIR}38_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 38 -e 38 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}38_tracedclean_v0.svg

${DATA_DIR}39_traced_v0.svg: ${DATA_DIR}39_pretrace_v1.svg
	rm -f ${DATA_DIR}39_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 39 -e 39 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}39_tracedclean_v0.svg

${DATA_DIR}40_traced_v0.svg: ${DATA_DIR}40_pretrace_v1.svg
	rm -f ${DATA_DIR}40_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 40 -e 40 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}40_tracedclean_v0.svg

${DATA_DIR}41_traced_v0.svg: ${DATA_DIR}41_pretrace_v1.svg
	rm -f ${DATA_DIR}41_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 41 -e 41 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}41_tracedclean_v0.svg

${DATA_DIR}42_traced_v0.svg: ${DATA_DIR}42_pretrace_v1.svg
	rm -f ${DATA_DIR}42_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 42 -e 42 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}42_tracedclean_v0.svg

${DATA_DIR}43_traced_v0.svg: ${DATA_DIR}43_pretrace_v1.svg
	rm -f ${DATA_DIR}43_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 43 -e 43 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}43_tracedclean_v0.svg

${DATA_DIR}44_traced_v0.svg: ${DATA_DIR}44_pretrace_v1.svg
	rm -f ${DATA_DIR}44_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 44 -e 44 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}44_tracedclean_v0.svg

${DATA_DIR}45_traced_v0.svg: ${DATA_DIR}45_pretrace_v1.svg
	rm -f ${DATA_DIR}45_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 45 -e 45 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}45_tracedclean_v0.svg

${DATA_DIR}46_traced_v0.svg: ${DATA_DIR}46_pretrace_v1.svg
	rm -f ${DATA_DIR}46_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 46 -e 46 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}46_tracedclean_v0.svg

${DATA_DIR}47_traced_v0.svg: ${DATA_DIR}47_pretrace_v1.svg
	rm -f ${DATA_DIR}47_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 47 -e 47 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}47_tracedclean_v0.svg

${DATA_DIR}48_traced_v0.svg: ${DATA_DIR}48_pretrace_v1.svg
	rm -f ${DATA_DIR}48_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 48 -e 48 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}48_tracedclean_v0.svg

${DATA_DIR}49_traced_v0.svg: ${DATA_DIR}49_pretrace_v1.svg
	rm -f ${DATA_DIR}49_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 49 -e 49 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}49_tracedclean_v0.svg

${DATA_DIR}50_traced_v0.svg: ${DATA_DIR}50_pretrace_v1.svg
	rm -f ${DATA_DIR}50_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 50 -e 50 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}50_tracedclean_v0.svg

${DATA_DIR}51_traced_v0.svg: ${DATA_DIR}51_pretrace_v1.svg
	rm -f ${DATA_DIR}51_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 51 -e 51 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}51_tracedclean_v0.svg

${DATA_DIR}52_traced_v0.svg: ${DATA_DIR}52_pretrace_v1.svg
	rm -f ${DATA_DIR}52_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 52 -e 52 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}52_tracedclean_v0.svg

${DATA_DIR}53_traced_v0.svg: ${DATA_DIR}53_pretrace_v1.svg
	rm -f ${DATA_DIR}53_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 53 -e 53 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}53_tracedclean_v0.svg

${DATA_DIR}54_traced_v0.svg: ${DATA_DIR}54_pretrace_v1.svg
	rm -f ${DATA_DIR}54_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 54 -e 54 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}54_tracedclean_v0.svg

${DATA_DIR}55_traced_v0.svg: ${DATA_DIR}55_pretrace_v1.svg
	rm -f ${DATA_DIR}55_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 55 -e 55 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}55_tracedclean_v0.svg

${DATA_DIR}56_traced_v0.svg: ${DATA_DIR}56_pretrace_v1.svg
	rm -f ${DATA_DIR}56_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 56 -e 56 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}56_tracedclean_v0.svg

${DATA_DIR}57_traced_v0.svg: ${DATA_DIR}57_pretrace_v1.svg
	rm -f ${DATA_DIR}57_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 57 -e 57 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}57_tracedclean_v0.svg

${DATA_DIR}58_traced_v0.svg: ${DATA_DIR}58_pretrace_v1.svg
	rm -f ${DATA_DIR}58_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 58 -e 58 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}58_tracedclean_v0.svg

${DATA_DIR}59_traced_v0.svg: ${DATA_DIR}59_pretrace_v1.svg
	rm -f ${DATA_DIR}59_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 59 -e 59 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}59_tracedclean_v0.svg

${DATA_DIR}60_traced_v0.svg: ${DATA_DIR}60_pretrace_v1.svg
	rm -f ${DATA_DIR}60_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 60 -e 60 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}60_tracedclean_v0.svg

${DATA_DIR}61_traced_v0.svg: ${DATA_DIR}61_pretrace_v1.svg
	rm -f ${DATA_DIR}61_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 61 -e 61 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}61_tracedclean_v0.svg

${DATA_DIR}62_traced_v0.svg: ${DATA_DIR}62_pretrace_v1.svg
	rm -f ${DATA_DIR}62_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 62 -e 62 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}62_tracedclean_v0.svg

${DATA_DIR}63_traced_v0.svg: ${DATA_DIR}63_pretrace_v1.svg
	rm -f ${DATA_DIR}63_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 63 -e 63 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}63_tracedclean_v0.svg

${DATA_DIR}64_traced_v0.svg: ${DATA_DIR}64_pretrace_v1.svg
	rm -f ${DATA_DIR}64_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 64 -e 64 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}64_tracedclean_v0.svg

${DATA_DIR}65_traced_v0.svg: ${DATA_DIR}65_pretrace_v1.svg
	rm -f ${DATA_DIR}65_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 65 -e 65 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}65_tracedclean_v0.svg

${DATA_DIR}66_traced_v0.svg: ${DATA_DIR}66_pretrace_v1.svg
	rm -f ${DATA_DIR}66_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 66 -e 66 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}66_tracedclean_v0.svg

${DATA_DIR}67_traced_v0.svg: ${DATA_DIR}67_pretrace_v1.svg
	rm -f ${DATA_DIR}67_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 67 -e 67 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}67_tracedclean_v0.svg

${DATA_DIR}68_traced_v0.svg: ${DATA_DIR}68_pretrace_v1.svg
	rm -f ${DATA_DIR}68_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 68 -e 68 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}68_tracedclean_v0.svg

${DATA_DIR}69_traced_v0.svg: ${DATA_DIR}69_pretrace_v1.svg
	rm -f ${DATA_DIR}69_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 69 -e 69 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}69_tracedclean_v0.svg

${DATA_DIR}70_traced_v0.svg: ${DATA_DIR}70_pretrace_v1.svg
	rm -f ${DATA_DIR}70_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 70 -e 70 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}70_tracedclean_v0.svg

${DATA_DIR}71_traced_v0.svg: ${DATA_DIR}71_pretrace_v1.svg
	rm -f ${DATA_DIR}71_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 71 -e 71 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}71_tracedclean_v0.svg

${DATA_DIR}72_traced_v0.svg: ${DATA_DIR}72_pretrace_v1.svg
	rm -f ${DATA_DIR}72_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 72 -e 72 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}72_tracedclean_v0.svg

${DATA_DIR}73_traced_v0.svg: ${DATA_DIR}73_pretrace_v1.svg
	rm -f ${DATA_DIR}73_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 73 -e 73 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}73_tracedclean_v0.svg

${DATA_DIR}74_traced_v0.svg: ${DATA_DIR}74_pretrace_v1.svg
	rm -f ${DATA_DIR}74_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 74 -e 74 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}74_tracedclean_v0.svg

${DATA_DIR}75_traced_v0.svg: ${DATA_DIR}75_pretrace_v1.svg
	rm -f ${DATA_DIR}75_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 75 -e 75 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}75_tracedclean_v0.svg

${DATA_DIR}76_traced_v0.svg: ${DATA_DIR}76_pretrace_v1.svg
	rm -f ${DATA_DIR}76_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 76 -e 76 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}76_tracedclean_v0.svg

${DATA_DIR}77_traced_v0.svg: ${DATA_DIR}77_pretrace_v1.svg
	rm -f ${DATA_DIR}77_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 77 -e 77 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}77_tracedclean_v0.svg

${DATA_DIR}78_traced_v0.svg: ${DATA_DIR}78_pretrace_v1.svg
	rm -f ${DATA_DIR}78_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 78 -e 78 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}78_tracedclean_v0.svg

${DATA_DIR}79_traced_v0.svg: ${DATA_DIR}79_pretrace_v1.svg
	rm -f ${DATA_DIR}79_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 79 -e 79 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}79_tracedclean_v0.svg

${DATA_DIR}80_traced_v0.svg: ${DATA_DIR}80_pretrace_v1.svg
	rm -f ${DATA_DIR}80_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 80 -e 80 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}80_tracedclean_v0.svg

${DATA_DIR}81_traced_v0.svg: ${DATA_DIR}81_pretrace_v1.svg
	rm -f ${DATA_DIR}81_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 81 -e 81 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}81_tracedclean_v0.svg

${DATA_DIR}82_traced_v0.svg: ${DATA_DIR}82_pretrace_v1.svg
	rm -f ${DATA_DIR}82_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 82 -e 82 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}82_tracedclean_v0.svg

${DATA_DIR}83_traced_v0.svg: ${DATA_DIR}83_pretrace_v1.svg
	rm -f ${DATA_DIR}83_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 83 -e 83 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}83_tracedclean_v0.svg

${DATA_DIR}84_traced_v0.svg: ${DATA_DIR}84_pretrace_v1.svg
	rm -f ${DATA_DIR}84_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 84 -e 84 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}84_tracedclean_v0.svg

${DATA_DIR}85_traced_v0.svg: ${DATA_DIR}85_pretrace_v1.svg
	rm -f ${DATA_DIR}85_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 85 -e 85 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}85_tracedclean_v0.svg

${DATA_DIR}86_traced_v0.svg: ${DATA_DIR}86_pretrace_v1.svg
	rm -f ${DATA_DIR}86_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 86 -e 86 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}86_tracedclean_v0.svg

${DATA_DIR}87_traced_v0.svg: ${DATA_DIR}87_pretrace_v1.svg
	rm -f ${DATA_DIR}87_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 87 -e 87 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}87_tracedclean_v0.svg

${DATA_DIR}88_traced_v0.svg: ${DATA_DIR}88_pretrace_v1.svg
	rm -f ${DATA_DIR}88_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 88 -e 88 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}88_tracedclean_v0.svg

${DATA_DIR}89_traced_v0.svg: ${DATA_DIR}89_pretrace_v1.svg
	rm -f ${DATA_DIR}89_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 89 -e 89 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}89_tracedclean_v0.svg

${DATA_DIR}90_traced_v0.svg: ${DATA_DIR}90_pretrace_v1.svg
	rm -f ${DATA_DIR}90_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 90 -e 90 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}90_tracedclean_v0.svg

${DATA_DIR}91_traced_v0.svg: ${DATA_DIR}91_pretrace_v1.svg
	rm -f ${DATA_DIR}91_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 91 -e 91 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}91_tracedclean_v0.svg

${DATA_DIR}92_traced_v0.svg: ${DATA_DIR}92_pretrace_v1.svg
	rm -f ${DATA_DIR}92_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 92 -e 92 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}92_tracedclean_v0.svg

${DATA_DIR}93_traced_v0.svg: ${DATA_DIR}93_pretrace_v1.svg
	rm -f ${DATA_DIR}93_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 93 -e 93 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}93_tracedclean_v0.svg

${DATA_DIR}94_traced_v0.svg: ${DATA_DIR}94_pretrace_v1.svg
	rm -f ${DATA_DIR}94_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 94 -e 94 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}94_tracedclean_v0.svg

${DATA_DIR}95_traced_v0.svg: ${DATA_DIR}95_pretrace_v1.svg
	rm -f ${DATA_DIR}95_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 95 -e 95 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}95_tracedclean_v0.svg

${DATA_DIR}96_traced_v0.svg: ${DATA_DIR}96_pretrace_v1.svg
	rm -f ${DATA_DIR}96_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 96 -e 96 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}96_tracedclean_v0.svg

${DATA_DIR}97_traced_v0.svg: ${DATA_DIR}97_pretrace_v1.svg
	rm -f ${DATA_DIR}97_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 97 -e 97 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}97_tracedclean_v0.svg

${DATA_DIR}98_traced_v0.svg: ${DATA_DIR}98_pretrace_v1.svg
	rm -f ${DATA_DIR}98_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 98 -e 98 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}98_tracedclean_v0.svg

${DATA_DIR}99_traced_v0.svg: ${DATA_DIR}99_pretrace_v1.svg
	rm -f ${DATA_DIR}99_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 99 -e 99 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}99_tracedclean_v0.svg

${DATA_DIR}100_traced_v0.svg: ${DATA_DIR}100_pretrace_v1.svg
	rm -f ${DATA_DIR}100_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 100 -e 100 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}100_tracedclean_v0.svg

${DATA_DIR}101_traced_v0.svg: ${DATA_DIR}101_pretrace_v1.svg
	rm -f ${DATA_DIR}101_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 101 -e 101 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}101_tracedclean_v0.svg

${DATA_DIR}102_traced_v0.svg: ${DATA_DIR}102_pretrace_v1.svg
	rm -f ${DATA_DIR}102_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 102 -e 102 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}102_tracedclean_v0.svg

${DATA_DIR}103_traced_v0.svg: ${DATA_DIR}103_pretrace_v1.svg
	rm -f ${DATA_DIR}103_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 103 -e 103 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}103_tracedclean_v0.svg

${DATA_DIR}104_traced_v0.svg: ${DATA_DIR}104_pretrace_v1.svg
	rm -f ${DATA_DIR}104_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 104 -e 104 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}104_tracedclean_v0.svg

${DATA_DIR}105_traced_v0.svg: ${DATA_DIR}105_pretrace_v1.svg
	rm -f ${DATA_DIR}105_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 105 -e 105 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}105_tracedclean_v0.svg

${DATA_DIR}106_traced_v0.svg: ${DATA_DIR}106_pretrace_v1.svg
	rm -f ${DATA_DIR}106_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 106 -e 106 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}106_tracedclean_v0.svg

${DATA_DIR}107_traced_v0.svg: ${DATA_DIR}107_pretrace_v1.svg
	rm -f ${DATA_DIR}107_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 107 -e 107 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}107_tracedclean_v0.svg

${DATA_DIR}108_traced_v0.svg: ${DATA_DIR}108_pretrace_v1.svg
	rm -f ${DATA_DIR}108_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 108 -e 108 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}108_tracedclean_v0.svg

${DATA_DIR}109_traced_v0.svg: ${DATA_DIR}109_pretrace_v1.svg
	rm -f ${DATA_DIR}109_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 109 -e 109 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}109_tracedclean_v0.svg

${DATA_DIR}110_traced_v0.svg: ${DATA_DIR}110_pretrace_v1.svg
	rm -f ${DATA_DIR}110_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 110 -e 110 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}110_tracedclean_v0.svg

${DATA_DIR}111_traced_v0.svg: ${DATA_DIR}111_pretrace_v1.svg
	rm -f ${DATA_DIR}111_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 111 -e 111 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}111_tracedclean_v0.svg

${DATA_DIR}112_traced_v0.svg: ${DATA_DIR}112_pretrace_v1.svg
	rm -f ${DATA_DIR}112_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 112 -e 112 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}112_tracedclean_v0.svg

${DATA_DIR}113_traced_v0.svg: ${DATA_DIR}113_pretrace_v1.svg
	rm -f ${DATA_DIR}113_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 113 -e 113 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}113_tracedclean_v0.svg

${DATA_DIR}114_traced_v0.svg: ${DATA_DIR}114_pretrace_v1.svg
	rm -f ${DATA_DIR}114_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 114 -e 114 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}114_tracedclean_v0.svg

${DATA_DIR}115_traced_v0.svg: ${DATA_DIR}115_pretrace_v1.svg
	rm -f ${DATA_DIR}115_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 115 -e 115 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}115_tracedclean_v0.svg

${DATA_DIR}116_traced_v0.svg: ${DATA_DIR}116_pretrace_v1.svg
	rm -f ${DATA_DIR}116_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 116 -e 116 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}116_tracedclean_v0.svg

${DATA_DIR}117_traced_v0.svg: ${DATA_DIR}117_pretrace_v1.svg
	rm -f ${DATA_DIR}117_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 117 -e 117 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}117_tracedclean_v0.svg

${DATA_DIR}118_traced_v0.svg: ${DATA_DIR}118_pretrace_v1.svg
	rm -f ${DATA_DIR}118_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 118 -e 118 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}118_tracedclean_v0.svg

${DATA_DIR}119_traced_v0.svg: ${DATA_DIR}119_pretrace_v1.svg
	rm -f ${DATA_DIR}119_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 119 -e 119 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}119_tracedclean_v0.svg

${DATA_DIR}120_traced_v0.svg: ${DATA_DIR}120_pretrace_v1.svg
	rm -f ${DATA_DIR}120_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 120 -e 120 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}120_tracedclean_v0.svg

${DATA_DIR}121_traced_v0.svg: ${DATA_DIR}121_pretrace_v1.svg
	rm -f ${DATA_DIR}121_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 121 -e 121 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}121_tracedclean_v0.svg

${DATA_DIR}122_traced_v0.svg: ${DATA_DIR}122_pretrace_v1.svg
	rm -f ${DATA_DIR}122_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 122 -e 122 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}122_tracedclean_v0.svg

${DATA_DIR}123_traced_v0.svg: ${DATA_DIR}123_pretrace_v1.svg
	rm -f ${DATA_DIR}123_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 123 -e 123 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}123_tracedclean_v0.svg

${DATA_DIR}124_traced_v0.svg: ${DATA_DIR}124_pretrace_v1.svg
	rm -f ${DATA_DIR}124_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 124 -e 124 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}124_tracedclean_v0.svg

${DATA_DIR}125_traced_v0.svg: ${DATA_DIR}125_pretrace_v1.svg
	rm -f ${DATA_DIR}125_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 125 -e 125 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}125_tracedclean_v0.svg

${DATA_DIR}126_traced_v0.svg: ${DATA_DIR}126_pretrace_v1.svg
	rm -f ${DATA_DIR}126_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 126 -e 126 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}126_tracedclean_v0.svg

${DATA_DIR}127_traced_v0.svg: ${DATA_DIR}127_pretrace_v1.svg
	rm -f ${DATA_DIR}127_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 127 -e 127 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}127_tracedclean_v0.svg

clean:
	rm -f ${DATA_DIR}*_traced_v0.svg
	rm -f ${DATA_DIR}*_tracedclean_v0.svg
