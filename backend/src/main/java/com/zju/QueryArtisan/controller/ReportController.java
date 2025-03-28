package com.zju.QueryArtisan.controller;

import com.zju.QueryArtisan.annotations.UserLoginToken;
import com.zju.QueryArtisan.entity.dataStruct.Response;
import com.zju.QueryArtisan.service.QueryService;
import com.zju.QueryArtisan.service.ReportService;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import javax.annotation.Resource;
import java.io.File;
import java.util.Map;

@RestController
@CrossOrigin(originPatterns = "*", allowCredentials = "true", maxAge = 3600)
public class ReportController {
    @Resource
    private ReportService reportService;

    @UserLoginToken
    @GetMapping("/api/Report/GetFullChat")
    public Response GetFullChat(@RequestParam String QueryId){
        return reportService.GetFullChat(QueryId);
    }

    @UserLoginToken
    @GetMapping("/api/Report/findData")
    public Response findData(String datasource){
        return reportService.findData(datasource);
    }

    @UserLoginToken
    @PostMapping("/api/Report/UploadDataFile")
    public Response UploadDataFile(
            @RequestParam("datasource") String datasource,
            @RequestParam("file") MultipartFile file
    ) {
        return reportService.UploadDataFile(datasource, file);
    }

    @UserLoginToken
    @GetMapping("/api/Report/FindDataSourceDeatils")
    public Response FindDataSourceDeatils(String datasource){
        return reportService.FindDataSourceDeatils(datasource);
    }

    @UserLoginToken
    @GetMapping("/api/Report/GetLogicalPlan")
    public Response GetLogicalPlan(@RequestParam String QueryId) {
        return reportService.GetLogicalPlan(QueryId);
    }

    @UserLoginToken
    @GetMapping("/api/Home/GetCode")
    public Response GetCode(@RequestParam String QueryId){
        return reportService.GetCode(QueryId);
    }

    @UserLoginToken
    @GetMapping("/api/Home/FlowChart_raw")
    public Response FlowChart_raw(@RequestParam String QueryId){
        return reportService.FlowChart_raw(QueryId);
    }

    @UserLoginToken
    @GetMapping("/api/Home/FlowChart_final")
    public Response FlowChart_final(@RequestParam String QueryId){
        return reportService.FlowChart_final(QueryId);
    }

    @UserLoginToken
    @GetMapping("/api/Report/read_datasource")
    public Response read_datasource(){
        return reportService.read_datasource();
    }

    @UserLoginToken
    @GetMapping("/api/Report/code_result")
    public Response code_result(@RequestParam String QueryId){
        return reportService.code_result(QueryId);
    }

    @UserLoginToken
    @GetMapping("/api/Report/Query_optimization_result")
    public Response Query_optimization_result(@RequestParam String QueryId){
        return reportService.Query_optimization_result(QueryId);
    }

    @UserLoginToken
    @PostMapping("/api/Report/lineageData")
    public Response getLineageData(@RequestBody Map<String, String> requestData) {
        String queryId = requestData.get("QueryId");
        String columnName = requestData.get("columnName");
        return reportService.getLineageData(queryId, columnName);
    }

    @UserLoginToken
    @PostMapping("/api/Report/getSourceData")
    public Response getSourceData(@RequestBody Map<String, String> requestData) {
        String tableName = requestData.get("tableName");
        return reportService.getSourceData(tableName);
    }

    @UserLoginToken
    @PostMapping("/api/Report/sendCommand")
    public Response sendCommand(@RequestBody Map<String, String> requestData) {
        String queryId = requestData.get("QueryId");
        String query = requestData.get("query");
        return reportService.sendCommand(queryId, query);
    }

    @UserLoginToken
    @GetMapping("/api/Report/getCommandHistory")
    public Response getCommandHistory(@RequestParam String QueryId) {
        return reportService.getCommandHistory(QueryId);
    }

}
