rem Run corese-server with dataset

java -jar "-Dfile.encoding=UTF8" "corese-server-4.5.0.jar" ^
	-l ./Zoomathia/annotations.ttl ^
	-l ./Zoomathia/paragraph.ttl ^
	-l ./Zoomathia/th310.ttl ^
	-l ./Zoomathia/paragraphs.ttl ^
	-l ./Zoomathia/metadata.ttl ^
	-l ./Zoomathia/link.ttl
