#
# python code for regenerating main code of this makefile:
# r=range(44,205)
#for i in r:
#    #print "${DATA_DIR}%d_traced_v0.svg\\" %i
#    print "${DATA_DIR}%d_traced_v0.svg: ${DATA_DIR}%d_pretrace_v1.svg" %(i,i)
#    print "\trm -f ${DATA_DIR}%d_traced_v0.svg" % i
#    print "\tpython parser_pax.py -p ${PARSER_NAME} -s %d -e %d -o ${DATA_DIR}"  %(i,i)
#    print "\tpython ${REGION_COMPARATOR} $@ ${DATA_DIR}%d_tracedclean_v0.svg" % i
#    print

PARSER_NAME = paxinos_watson_rbisc
PARSERS_DIR = bin/parsers/${PARSER_NAME}/
ATLAS_DIR = atlases/atlases_separated/${PARSER_NAME}/
DATA_DIR  = ${ATLAS_DIR}caf-src/
REGION_COMPARATOR = ${PARSERS_DIR}region_comparator.py

${DATA_DIR}index.xml: ${DATA_DIR}parents.txt ${DATA_DIR}fullnames.txt slides
	touch ${DATA_DIR}*_traced*v*.svg
	python parser_pax.py -p ${PARSER_NAME} -s 44 -e 204 --create-only-index-file  -o ${DATA_DIR} -i ${DATA_DIR}

all: slides ${DATA_DIR}index.xml
	echo "Done processing"

slides: ${DATA_DIR}44_traced_v0.svg ${DATA_DIR}45_traced_v0.svg\
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
	${DATA_DIR}126_traced_v0.svg ${DATA_DIR}127_traced_v0.svg\
	${DATA_DIR}128_traced_v0.svg ${DATA_DIR}129_traced_v0.svg\
	${DATA_DIR}130_traced_v0.svg ${DATA_DIR}131_traced_v0.svg\
	${DATA_DIR}132_traced_v0.svg ${DATA_DIR}133_traced_v0.svg\
	${DATA_DIR}134_traced_v0.svg ${DATA_DIR}135_traced_v0.svg\
	${DATA_DIR}136_traced_v0.svg ${DATA_DIR}137_traced_v0.svg\
	${DATA_DIR}138_traced_v0.svg ${DATA_DIR}139_traced_v0.svg\
	${DATA_DIR}140_traced_v0.svg ${DATA_DIR}141_traced_v0.svg\
	${DATA_DIR}142_traced_v0.svg ${DATA_DIR}143_traced_v0.svg\
	${DATA_DIR}144_traced_v0.svg ${DATA_DIR}145_traced_v0.svg\
	${DATA_DIR}146_traced_v0.svg ${DATA_DIR}147_traced_v0.svg\
	${DATA_DIR}148_traced_v0.svg ${DATA_DIR}149_traced_v0.svg\
	${DATA_DIR}150_traced_v0.svg ${DATA_DIR}151_traced_v0.svg\
	${DATA_DIR}152_traced_v0.svg ${DATA_DIR}153_traced_v0.svg\
	${DATA_DIR}154_traced_v0.svg ${DATA_DIR}155_traced_v0.svg\
	${DATA_DIR}156_traced_v0.svg ${DATA_DIR}157_traced_v0.svg\
	${DATA_DIR}158_traced_v0.svg ${DATA_DIR}159_traced_v0.svg\
	${DATA_DIR}160_traced_v0.svg ${DATA_DIR}161_traced_v0.svg\
	${DATA_DIR}162_traced_v0.svg ${DATA_DIR}163_traced_v0.svg\
	${DATA_DIR}164_traced_v0.svg ${DATA_DIR}165_traced_v0.svg\
	${DATA_DIR}166_traced_v0.svg ${DATA_DIR}167_traced_v0.svg\
	${DATA_DIR}168_traced_v0.svg ${DATA_DIR}169_traced_v0.svg\
	${DATA_DIR}170_traced_v0.svg ${DATA_DIR}171_traced_v0.svg\
	${DATA_DIR}172_traced_v0.svg ${DATA_DIR}173_traced_v0.svg\
	${DATA_DIR}174_traced_v0.svg ${DATA_DIR}175_traced_v0.svg\
	${DATA_DIR}176_traced_v0.svg ${DATA_DIR}177_traced_v0.svg\
	${DATA_DIR}178_traced_v0.svg ${DATA_DIR}179_traced_v0.svg\
	${DATA_DIR}180_traced_v0.svg ${DATA_DIR}181_traced_v0.svg\
	${DATA_DIR}182_traced_v0.svg ${DATA_DIR}183_traced_v0.svg\
	${DATA_DIR}184_traced_v0.svg ${DATA_DIR}185_traced_v0.svg\
	${DATA_DIR}186_traced_v0.svg ${DATA_DIR}187_traced_v0.svg\
	${DATA_DIR}188_traced_v0.svg ${DATA_DIR}189_traced_v0.svg\
	${DATA_DIR}190_traced_v0.svg ${DATA_DIR}191_traced_v0.svg\
	${DATA_DIR}192_traced_v0.svg ${DATA_DIR}193_traced_v0.svg\
	${DATA_DIR}194_traced_v0.svg ${DATA_DIR}195_traced_v0.svg\
	${DATA_DIR}196_traced_v0.svg ${DATA_DIR}197_traced_v0.svg\
	${DATA_DIR}198_traced_v0.svg ${DATA_DIR}199_traced_v0.svg\
	${DATA_DIR}200_traced_v0.svg ${DATA_DIR}201_traced_v0.svg\
	${DATA_DIR}202_traced_v0.svg ${DATA_DIR}203_traced_v0.svg\
	${DATA_DIR}204_traced_v0.svg

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

${DATA_DIR}128_traced_v0.svg: ${DATA_DIR}128_pretrace_v1.svg
	rm -f ${DATA_DIR}128_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 128 -e 128 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}128_tracedclean_v0.svg

${DATA_DIR}129_traced_v0.svg: ${DATA_DIR}129_pretrace_v1.svg
	rm -f ${DATA_DIR}129_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 129 -e 129 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}129_tracedclean_v0.svg

${DATA_DIR}130_traced_v0.svg: ${DATA_DIR}130_pretrace_v1.svg
	rm -f ${DATA_DIR}130_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 130 -e 130 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}130_tracedclean_v0.svg

${DATA_DIR}131_traced_v0.svg: ${DATA_DIR}131_pretrace_v1.svg
	rm -f ${DATA_DIR}131_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 131 -e 131 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}131_tracedclean_v0.svg

${DATA_DIR}132_traced_v0.svg: ${DATA_DIR}132_pretrace_v1.svg
	rm -f ${DATA_DIR}132_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 132 -e 132 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}132_tracedclean_v0.svg

${DATA_DIR}133_traced_v0.svg: ${DATA_DIR}133_pretrace_v1.svg
	rm -f ${DATA_DIR}133_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 133 -e 133 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}133_tracedclean_v0.svg

${DATA_DIR}134_traced_v0.svg: ${DATA_DIR}134_pretrace_v1.svg
	rm -f ${DATA_DIR}134_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 134 -e 134 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}134_tracedclean_v0.svg

${DATA_DIR}135_traced_v0.svg: ${DATA_DIR}135_pretrace_v1.svg
	rm -f ${DATA_DIR}135_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 135 -e 135 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}135_tracedclean_v0.svg

${DATA_DIR}136_traced_v0.svg: ${DATA_DIR}136_pretrace_v1.svg
	rm -f ${DATA_DIR}136_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 136 -e 136 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}136_tracedclean_v0.svg

${DATA_DIR}137_traced_v0.svg: ${DATA_DIR}137_pretrace_v1.svg
	rm -f ${DATA_DIR}137_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 137 -e 137 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}137_tracedclean_v0.svg

${DATA_DIR}138_traced_v0.svg: ${DATA_DIR}138_pretrace_v1.svg
	rm -f ${DATA_DIR}138_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 138 -e 138 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}138_tracedclean_v0.svg

${DATA_DIR}139_traced_v0.svg: ${DATA_DIR}139_pretrace_v1.svg
	rm -f ${DATA_DIR}139_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 139 -e 139 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}139_tracedclean_v0.svg

${DATA_DIR}140_traced_v0.svg: ${DATA_DIR}140_pretrace_v1.svg
	rm -f ${DATA_DIR}140_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 140 -e 140 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}140_tracedclean_v0.svg

${DATA_DIR}141_traced_v0.svg: ${DATA_DIR}141_pretrace_v1.svg
	rm -f ${DATA_DIR}141_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 141 -e 141 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}141_tracedclean_v0.svg

${DATA_DIR}142_traced_v0.svg: ${DATA_DIR}142_pretrace_v1.svg
	rm -f ${DATA_DIR}142_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 142 -e 142 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}142_tracedclean_v0.svg

${DATA_DIR}143_traced_v0.svg: ${DATA_DIR}143_pretrace_v1.svg
	rm -f ${DATA_DIR}143_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 143 -e 143 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}143_tracedclean_v0.svg

${DATA_DIR}144_traced_v0.svg: ${DATA_DIR}144_pretrace_v1.svg
	rm -f ${DATA_DIR}144_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 144 -e 144 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}144_tracedclean_v0.svg

${DATA_DIR}145_traced_v0.svg: ${DATA_DIR}145_pretrace_v1.svg
	rm -f ${DATA_DIR}145_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 145 -e 145 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}145_tracedclean_v0.svg

${DATA_DIR}146_traced_v0.svg: ${DATA_DIR}146_pretrace_v1.svg
	rm -f ${DATA_DIR}146_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 146 -e 146 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}146_tracedclean_v0.svg

${DATA_DIR}147_traced_v0.svg: ${DATA_DIR}147_pretrace_v1.svg
	rm -f ${DATA_DIR}147_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 147 -e 147 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}147_tracedclean_v0.svg

${DATA_DIR}148_traced_v0.svg: ${DATA_DIR}148_pretrace_v1.svg
	rm -f ${DATA_DIR}148_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 148 -e 148 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}148_tracedclean_v0.svg

${DATA_DIR}149_traced_v0.svg: ${DATA_DIR}149_pretrace_v1.svg
	rm -f ${DATA_DIR}149_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 149 -e 149 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}149_tracedclean_v0.svg

${DATA_DIR}150_traced_v0.svg: ${DATA_DIR}150_pretrace_v1.svg
	rm -f ${DATA_DIR}150_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 150 -e 150 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}150_tracedclean_v0.svg

${DATA_DIR}151_traced_v0.svg: ${DATA_DIR}151_pretrace_v1.svg
	rm -f ${DATA_DIR}151_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 151 -e 151 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}151_tracedclean_v0.svg

${DATA_DIR}152_traced_v0.svg: ${DATA_DIR}152_pretrace_v1.svg
	rm -f ${DATA_DIR}152_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 152 -e 152 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}152_tracedclean_v0.svg

${DATA_DIR}153_traced_v0.svg: ${DATA_DIR}153_pretrace_v1.svg
	rm -f ${DATA_DIR}153_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 153 -e 153 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}153_tracedclean_v0.svg

${DATA_DIR}154_traced_v0.svg: ${DATA_DIR}154_pretrace_v1.svg
	rm -f ${DATA_DIR}154_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 154 -e 154 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}154_tracedclean_v0.svg

${DATA_DIR}155_traced_v0.svg: ${DATA_DIR}155_pretrace_v1.svg
	rm -f ${DATA_DIR}155_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 155 -e 155 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}155_tracedclean_v0.svg

${DATA_DIR}156_traced_v0.svg: ${DATA_DIR}156_pretrace_v1.svg
	rm -f ${DATA_DIR}156_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 156 -e 156 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}156_tracedclean_v0.svg

${DATA_DIR}157_traced_v0.svg: ${DATA_DIR}157_pretrace_v1.svg
	rm -f ${DATA_DIR}157_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 157 -e 157 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}157_tracedclean_v0.svg

${DATA_DIR}158_traced_v0.svg: ${DATA_DIR}158_pretrace_v1.svg
	rm -f ${DATA_DIR}158_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 158 -e 158 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}158_tracedclean_v0.svg

${DATA_DIR}159_traced_v0.svg: ${DATA_DIR}159_pretrace_v1.svg
	rm -f ${DATA_DIR}159_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 159 -e 159 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}159_tracedclean_v0.svg

${DATA_DIR}160_traced_v0.svg: ${DATA_DIR}160_pretrace_v1.svg
	rm -f ${DATA_DIR}160_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 160 -e 160 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}160_tracedclean_v0.svg

${DATA_DIR}161_traced_v0.svg: ${DATA_DIR}161_pretrace_v1.svg
	rm -f ${DATA_DIR}161_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 161 -e 161 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}161_tracedclean_v0.svg

${DATA_DIR}162_traced_v0.svg: ${DATA_DIR}162_pretrace_v1.svg
	rm -f ${DATA_DIR}162_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 162 -e 162 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}162_tracedclean_v0.svg

${DATA_DIR}163_traced_v0.svg: ${DATA_DIR}163_pretrace_v1.svg
	rm -f ${DATA_DIR}163_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 163 -e 163 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}163_tracedclean_v0.svg

${DATA_DIR}164_traced_v0.svg: ${DATA_DIR}164_pretrace_v1.svg
	rm -f ${DATA_DIR}164_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 164 -e 164 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}164_tracedclean_v0.svg

${DATA_DIR}165_traced_v0.svg: ${DATA_DIR}165_pretrace_v1.svg
	rm -f ${DATA_DIR}165_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 165 -e 165 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}165_tracedclean_v0.svg

${DATA_DIR}166_traced_v0.svg: ${DATA_DIR}166_pretrace_v1.svg
	rm -f ${DATA_DIR}166_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 166 -e 166 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}166_tracedclean_v0.svg

${DATA_DIR}167_traced_v0.svg: ${DATA_DIR}167_pretrace_v1.svg
	rm -f ${DATA_DIR}167_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 167 -e 167 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}167_tracedclean_v0.svg

${DATA_DIR}168_traced_v0.svg: ${DATA_DIR}168_pretrace_v1.svg
	rm -f ${DATA_DIR}168_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 168 -e 168 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}168_tracedclean_v0.svg

${DATA_DIR}169_traced_v0.svg: ${DATA_DIR}169_pretrace_v1.svg
	rm -f ${DATA_DIR}169_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 169 -e 169 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}169_tracedclean_v0.svg

${DATA_DIR}170_traced_v0.svg: ${DATA_DIR}170_pretrace_v1.svg
	rm -f ${DATA_DIR}170_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 170 -e 170 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}170_tracedclean_v0.svg

${DATA_DIR}171_traced_v0.svg: ${DATA_DIR}171_pretrace_v1.svg
	rm -f ${DATA_DIR}171_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 171 -e 171 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}171_tracedclean_v0.svg

${DATA_DIR}172_traced_v0.svg: ${DATA_DIR}172_pretrace_v1.svg
	rm -f ${DATA_DIR}172_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 172 -e 172 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}172_tracedclean_v0.svg

${DATA_DIR}173_traced_v0.svg: ${DATA_DIR}173_pretrace_v1.svg
	rm -f ${DATA_DIR}173_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 173 -e 173 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}173_tracedclean_v0.svg

${DATA_DIR}174_traced_v0.svg: ${DATA_DIR}174_pretrace_v1.svg
	rm -f ${DATA_DIR}174_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 174 -e 174 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}174_tracedclean_v0.svg

${DATA_DIR}175_traced_v0.svg: ${DATA_DIR}175_pretrace_v1.svg
	rm -f ${DATA_DIR}175_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 175 -e 175 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}175_tracedclean_v0.svg

${DATA_DIR}176_traced_v0.svg: ${DATA_DIR}176_pretrace_v1.svg
	rm -f ${DATA_DIR}176_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 176 -e 176 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}176_tracedclean_v0.svg

${DATA_DIR}177_traced_v0.svg: ${DATA_DIR}177_pretrace_v1.svg
	rm -f ${DATA_DIR}177_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 177 -e 177 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}177_tracedclean_v0.svg

${DATA_DIR}178_traced_v0.svg: ${DATA_DIR}178_pretrace_v1.svg
	rm -f ${DATA_DIR}178_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 178 -e 178 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}178_tracedclean_v0.svg

${DATA_DIR}179_traced_v0.svg: ${DATA_DIR}179_pretrace_v1.svg
	rm -f ${DATA_DIR}179_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 179 -e 179 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}179_tracedclean_v0.svg

${DATA_DIR}180_traced_v0.svg: ${DATA_DIR}180_pretrace_v1.svg
	rm -f ${DATA_DIR}180_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 180 -e 180 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}180_tracedclean_v0.svg

${DATA_DIR}181_traced_v0.svg: ${DATA_DIR}181_pretrace_v1.svg
	rm -f ${DATA_DIR}181_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 181 -e 181 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}181_tracedclean_v0.svg

${DATA_DIR}182_traced_v0.svg: ${DATA_DIR}182_pretrace_v1.svg
	rm -f ${DATA_DIR}182_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 182 -e 182 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}182_tracedclean_v0.svg

${DATA_DIR}183_traced_v0.svg: ${DATA_DIR}183_pretrace_v1.svg
	rm -f ${DATA_DIR}183_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 183 -e 183 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}183_tracedclean_v0.svg

${DATA_DIR}184_traced_v0.svg: ${DATA_DIR}184_pretrace_v1.svg
	rm -f ${DATA_DIR}184_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 184 -e 184 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}184_tracedclean_v0.svg

${DATA_DIR}185_traced_v0.svg: ${DATA_DIR}185_pretrace_v1.svg
	rm -f ${DATA_DIR}185_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 185 -e 185 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}185_tracedclean_v0.svg

${DATA_DIR}186_traced_v0.svg: ${DATA_DIR}186_pretrace_v1.svg
	rm -f ${DATA_DIR}186_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 186 -e 186 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}186_tracedclean_v0.svg

${DATA_DIR}187_traced_v0.svg: ${DATA_DIR}187_pretrace_v1.svg
	rm -f ${DATA_DIR}187_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 187 -e 187 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}187_tracedclean_v0.svg

${DATA_DIR}188_traced_v0.svg: ${DATA_DIR}188_pretrace_v1.svg
	rm -f ${DATA_DIR}188_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 188 -e 188 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}188_tracedclean_v0.svg

${DATA_DIR}189_traced_v0.svg: ${DATA_DIR}189_pretrace_v1.svg
	rm -f ${DATA_DIR}189_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 189 -e 189 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}189_tracedclean_v0.svg

${DATA_DIR}190_traced_v0.svg: ${DATA_DIR}190_pretrace_v1.svg
	rm -f ${DATA_DIR}190_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 190 -e 190 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}190_tracedclean_v0.svg

${DATA_DIR}191_traced_v0.svg: ${DATA_DIR}191_pretrace_v1.svg
	rm -f ${DATA_DIR}191_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 191 -e 191 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}191_tracedclean_v0.svg

${DATA_DIR}192_traced_v0.svg: ${DATA_DIR}192_pretrace_v1.svg
	rm -f ${DATA_DIR}192_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 192 -e 192 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}192_tracedclean_v0.svg

${DATA_DIR}193_traced_v0.svg: ${DATA_DIR}193_pretrace_v1.svg
	rm -f ${DATA_DIR}193_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 193 -e 193 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}193_tracedclean_v0.svg

${DATA_DIR}194_traced_v0.svg: ${DATA_DIR}194_pretrace_v1.svg
	rm -f ${DATA_DIR}194_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 194 -e 194 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}194_tracedclean_v0.svg

${DATA_DIR}195_traced_v0.svg: ${DATA_DIR}195_pretrace_v1.svg
	rm -f ${DATA_DIR}195_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 195 -e 195 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}195_tracedclean_v0.svg

${DATA_DIR}196_traced_v0.svg: ${DATA_DIR}196_pretrace_v1.svg
	rm -f ${DATA_DIR}196_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 196 -e 196 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}196_tracedclean_v0.svg

${DATA_DIR}197_traced_v0.svg: ${DATA_DIR}197_pretrace_v1.svg
	rm -f ${DATA_DIR}197_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 197 -e 197 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}197_tracedclean_v0.svg

${DATA_DIR}198_traced_v0.svg: ${DATA_DIR}198_pretrace_v1.svg
	rm -f ${DATA_DIR}198_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 198 -e 198 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}198_tracedclean_v0.svg

${DATA_DIR}199_traced_v0.svg: ${DATA_DIR}199_pretrace_v1.svg
	rm -f ${DATA_DIR}199_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 199 -e 199 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}199_tracedclean_v0.svg

${DATA_DIR}200_traced_v0.svg: ${DATA_DIR}200_pretrace_v1.svg
	rm -f ${DATA_DIR}200_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 200 -e 200 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}200_tracedclean_v0.svg

${DATA_DIR}201_traced_v0.svg: ${DATA_DIR}201_pretrace_v1.svg
	rm -f ${DATA_DIR}201_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 201 -e 201 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}201_tracedclean_v0.svg

${DATA_DIR}202_traced_v0.svg: ${DATA_DIR}202_pretrace_v1.svg
	rm -f ${DATA_DIR}202_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 202 -e 202 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}202_tracedclean_v0.svg

${DATA_DIR}203_traced_v0.svg: ${DATA_DIR}203_pretrace_v1.svg
	rm -f ${DATA_DIR}203_traced_v0.svg
	python parser_pax.py -p ${PARSER_NAME} -s 203 -e 203 -o ${DATA_DIR} -i ${DATA_DIR}
	python ${REGION_COMPARATOR} $@ ${DATA_DIR}203_tracedclean_v0.svg

clean:
	rm -f ${DATA_DIR}*_traced_v0.svg
	rm -f ${DATA_DIR}*_tracedclean_v0.svg
