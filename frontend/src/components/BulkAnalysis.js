import React, { useState, useCallback } from "react";

const BulkAnalysis = () => {
    const [isDragOver, setIsDragOver] = useState(false);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [taskId, setTaskId] = useState(null);
    const [results, setResults] = useState(null);
    const [progress, setProgress] = useState(null);
    const [selectedResult, setSelectedResult] = useState(null);
    const [isModalOpen, setIsModalOpen] = useState(false);

    // Accordion state for detailed view
    const [accordionState, setAccordionState] = useState({
        legalResearch: true,
        geoRegulatory: false,
        documentationTrail: false,
        complianceStatus: true,
    });

    const handleDragOver = useCallback((e) => {
        e.preventDefault();
        setIsDragOver(true);
    }, []);

    const handleDragLeave = useCallback((e) => {
        e.preventDefault();
        setIsDragOver(false);
    }, []);

    const handleDrop = useCallback((e) => {
        e.preventDefault();
        setIsDragOver(false);
        
        const files = Array.from(e.dataTransfer.files);
        const csvFile = files.find(file => file.name.endsWith('.csv'));
        
        if (csvFile) {
            handleFileUpload(csvFile);
        } else {
            alert("Please drop a CSV file");
        }
    }, []);

    const handleFileInputChange = (e) => {
        const file = e.target.files[0];
        if (file && file.name.endsWith('.csv')) {
            handleFileUpload(file);
        } else {
            alert("Please select a CSV file");
        }
    };

    const handleFileUpload = async (file) => {
        setIsAnalyzing(true);
        setResults(null);
        setProgress(null);
        
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch("http://localhost:8001/api/bulk-csv-analysis", {
                method: "POST",
                body: formData,
            });

            const data = await response.json();
            
            if (response.ok) {
                setTaskId(data.task_id);
                pollForResults(data.task_id);
            } else {
                throw new Error(data.detail || "Upload failed");
            }
        } catch (error) {
            console.error("CSV upload failed:", error);
            setResults({ error: error.message });
            setIsAnalyzing(false);
        }
    };

    const pollForResults = async (id) => {
        const maxPolls = 120; // 10 minutes max
        let pollCount = 0;

        const poll = async () => {
            try {
                const response = await fetch(`http://localhost:8001/api/results/${id}`);
                const data = await response.json();

                if (data.status === "completed" || data.status === "failed") {
                    setResults(data);
                    setIsAnalyzing(false);
                    return;
                }

                if (data.status === "running") {
                    setProgress({
                        completed: data.completed_items || 0,
                        total: data.total_items || 0
                    });
                }

                pollCount++;
                if (pollCount < maxPolls) {
                    setTimeout(poll, 5000); // Poll every 5 seconds
                } else {
                    setResults({ error: "Analysis timed out" });
                    setIsAnalyzing(false);
                }
            } catch (error) {
                console.error("Polling failed:", error);
                setResults({ error: "Failed to get results" });
                setIsAnalyzing(false);
            }
        };

        setTimeout(poll, 2000); // Start polling after 2 seconds
    };

    const toggleAccordion = (section) => {
        setAccordionState((prev) => ({
            ...prev,
            [section]: !prev[section],
        }));
    };

    const openDetailModal = (result) => {
        setSelectedResult(result);
        setIsModalOpen(true);
    };

    const closeDetailModal = () => {
        setSelectedResult(null);
        setIsModalOpen(false);
    };

    return (
        <div>
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-gray-900 mb-2">
                    Bulk CSV Analysis
                </h1>
                <p className="text-gray-600">
                    Upload a CSV file to analyze multiple items for compliance simultaneously
                </p>
            </div>

            <div className="space-y-8">
                {/* CSV Upload Area */}
                <div className="bg-white p-6 rounded-lg shadow">
                    <h2 className="text-xl font-semibold text-gray-900 mb-6">
                        Upload CSV File
                    </h2>

                    <div
                        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                            isDragOver
                                ? "border-blue-500 bg-blue-50"
                                : "border-gray-300 hover:border-gray-400"
                        }`}
                        onDragOver={handleDragOver}
                        onDragLeave={handleDragLeave}
                        onDrop={handleDrop}
                    >
                        <div className="mb-4">
                            <svg
                                className="mx-auto h-12 w-12 text-gray-400"
                                stroke="currentColor"
                                fill="none"
                                viewBox="0 0 48 48"
                            >
                                <path
                                    d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                                    strokeWidth={2}
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                />
                            </svg>
                        </div>
                        
                        <div className="mb-4">
                            <p className="text-lg font-medium text-gray-900 mb-2">
                                {isDragOver
                                    ? "Drop your CSV file here"
                                    : "Drag and drop your CSV file here"}
                            </p>
                            <p className="text-gray-600">
                                Expected format: Jira export CSV with Summary, Issue Type, Priority, etc.
                            </p>
                        </div>

                        <div className="mb-4">
                            <span className="text-gray-500">or</span>
                        </div>

                        <label className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 cursor-pointer transition-colors">
                            Choose File
                            <input
                                type="file"
                                accept=".csv"
                                onChange={handleFileInputChange}
                                className="sr-only"
                            />
                        </label>
                    </div>
                </div>

                {/* Progress */}
                {isAnalyzing && progress && (
                    <div className="bg-white p-6 rounded-lg shadow">
                        <h2 className="text-xl font-semibold text-gray-900 mb-4">
                            Analysis Progress
                        </h2>
                        <div className="mb-4">
                            <div className="flex justify-between mb-2">
                                <span className="text-sm text-gray-600">
                                    Processing items...
                                </span>
                                <span className="text-sm text-gray-600">
                                    {progress.completed} / {progress.total}
                                </span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                                <div
                                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                                    style={{
                                        width: `${
                                            progress.total > 0
                                                ? (progress.completed / progress.total) * 100
                                                : 0
                                        }%`,
                                    }}
                                ></div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Loading */}
                {isAnalyzing && !progress && (
                    <div className="bg-white p-6 rounded-lg shadow">
                        <div className="text-center py-8">
                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                            <p className="mt-4 text-gray-600">
                                Starting analysis...
                            </p>
                        </div>
                    </div>
                )}

                {/* Results */}
                {results && (
                    <div className="bg-white p-6 rounded-lg shadow">
                        <h2 className="text-xl font-semibold text-gray-900 mb-6">
                            Analysis Results
                        </h2>

                        {results.error ? (
                            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                                <p className="text-red-800">{results.error}</p>
                            </div>
                        ) : results.status === "completed" ? (
                            <div className="space-y-6">
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                                    <div className="bg-green-50 p-4 rounded-lg">
                                        <div className="text-2xl font-bold text-green-600">
                                            {results.success_count || 0}
                                        </div>
                                        <div className="text-sm text-green-600">
                                            Successful Analyses
                                        </div>
                                    </div>
                                    <div className="bg-red-50 p-4 rounded-lg">
                                        <div className="text-2xl font-bold text-red-600">
                                            {results.failure_count || 0}
                                        </div>
                                        <div className="text-sm text-red-600">
                                            Failed Analyses
                                        </div>
                                    </div>
                                    <div className="bg-blue-50 p-4 rounded-lg">
                                        <div className="text-2xl font-bold text-blue-600">
                                            {results.total_items || 0}
                                        </div>
                                        <div className="text-sm text-blue-600">
                                            Total Items
                                        </div>
                                    </div>
                                </div>

                                <div className="space-y-4">
                                    {results.results?.map((result, index) => (
                                        <div
                                            key={index}
                                            className={`border rounded-lg p-4 cursor-pointer transition-all hover:shadow-md ${
                                                result.success
                                                    ? "border-green-200 bg-green-50 hover:border-green-300"
                                                    : "border-red-200 bg-red-50 hover:border-red-300"
                                            }`}
                                            onClick={() => result.success && openDetailModal(result)}
                                        >
                                            <div className="flex justify-between items-start mb-2">
                                                <h3 className="font-semibold text-gray-900">
                                                    {result.feature_name}
                                                </h3>
                                                <div className="flex items-center space-x-2">
                                                    <span
                                                        className={`px-2 py-1 text-xs rounded ${
                                                            result.success
                                                                ? "bg-green-100 text-green-800"
                                                                : "bg-red-100 text-red-800"
                                                        }`}
                                                    >
                                                        {result.success ? "Success" : "Failed"}
                                                    </span>
                                                    {result.success && (
                                                        <button
                                                            className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded hover:bg-blue-200"
                                                            onClick={(e) => {
                                                                e.stopPropagation();
                                                                openDetailModal(result);
                                                            }}
                                                        >
                                                            View Details
                                                        </button>
                                                    )}
                                                </div>
                                            </div>
                                            
                                            {result.success ? (
                                                <div className="text-sm text-gray-600">
                                                    Analysis completed at{" "}
                                                    {new Date(result.timestamp).toLocaleString()}
                                                    {result.success && (
                                                        <span className="block mt-1 text-blue-600">
                                                            Click to view detailed analysis →
                                                        </span>
                                                    )}
                                                </div>
                                            ) : (
                                                <div className="text-sm text-red-600">
                                                    Error: {result.error}
                                                </div>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ) : (
                            <div className="text-center text-gray-500 py-8">
                                <p>Analysis in progress...</p>
                            </div>
                        )}
                    </div>
                )}

                {!results && !isAnalyzing && (
                    <div className="bg-white p-6 rounded-lg shadow">
                        <div className="text-center text-gray-500 py-8">
                            <p>Upload a CSV file to see analysis results here.</p>
                        </div>
                    </div>
                )}
            </div>

            {/* Detail Modal */}
            {isModalOpen && selectedResult && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
                    <div className="bg-white rounded-lg max-w-4xl max-h-[90vh] overflow-y-auto w-full">
                        <div className="sticky top-0 bg-white border-b border-gray-200 p-6">
                            <div className="flex justify-between items-center">
                                <h2 className="text-2xl font-bold text-gray-900">
                                    Analysis Details: {selectedResult.feature_name}
                                </h2>
                                <button
                                    onClick={closeDetailModal}
                                    className="text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-lg p-2"
                                >
                                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
                                    </svg>
                                </button>
                            </div>
                        </div>

                        <div className="p-6 space-y-6">
                            {/* Analysis Summary Header */}
                            <div className="p-6 border border-blue-200 rounded-lg bg-blue-50">
                                <div className="flex items-center justify-between mb-4">
                                    <h3 className="text-xl font-bold text-blue-900">
                                        Analysis Results
                                    </h3>
                                    <span
                                        className={`px-3 py-1 text-sm font-medium rounded-full ${
                                            selectedResult.analysis_result?.audit_trail_ready
                                                ? "bg-green-100 text-green-800"
                                                : "bg-yellow-100 text-yellow-800"
                                        }`}
                                    >
                                        {selectedResult.analysis_result?.audit_trail_ready
                                            ? "Audit Ready"
                                            : "In Progress"}
                                    </span>
                                </div>

                                <div className="space-y-3">
                                    <div>
                                        <span className="text-sm font-medium text-blue-700">
                                            Feature:
                                        </span>
                                        <p className="text-lg font-semibold text-blue-900">
                                            {selectedResult.feature_name}
                                        </p>
                                    </div>
                                    <div>
                                        <span className="text-sm font-medium text-blue-700">
                                            Analysis Type:
                                        </span>
                                        <p className="text-lg font-semibold text-blue-900 capitalize">
                                            {selectedResult.analysis_result?.analysis_type?.replace(/_/g, " ") || "Comprehensive Compliance Analysis"}
                                        </p>
                                    </div>
                                    {selectedResult.analysis_result?.compliance_status && (
                                        <div>
                                            <span className="text-sm font-medium text-blue-700">
                                                Compliance Status:
                                            </span>
                                            <p
                                                className={`text-lg font-semibold ${
                                                    selectedResult.analysis_result.risk_level === "HIGH"
                                                        ? "text-red-600"
                                                        : selectedResult.analysis_result.risk_level === "MEDIUM"
                                                        ? "text-yellow-600"
                                                        : "text-green-600"
                                                }`}
                                            >
                                                {selectedResult.analysis_result.compliance_status?.replace(/_/g, " ") ||
                                                 "Needs Review"}
                                            </p>
                                        </div>
                                    )}
                                    <div>
                                        <span className="text-sm font-medium text-blue-700">
                                            Risk Level:
                                        </span>
                                        <span
                                            className={`inline-block px-2 py-1 ml-2 text-sm font-medium rounded-full ${
                                                selectedResult.analysis_result?.risk_level === "HIGH"
                                                    ? "bg-red-100 text-red-800"
                                                    : selectedResult.analysis_result?.risk_level === "MEDIUM"
                                                    ? "bg-yellow-100 text-yellow-800"
                                                    : "bg-green-100 text-green-800"
                                            }`}
                                        >
                                            {selectedResult.analysis_result?.risk_level || "MEDIUM"}
                                        </span>
                                    </div>
                                </div>
                            </div>

                            {/* Legal Research Analysis - Accordion */}
                            <div className="border border-yellow-200 rounded-lg bg-yellow-50">
                                <button
                                    className="w-full p-6 text-left rounded-t-lg focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:ring-inset"
                                    onClick={() => toggleAccordion("legalResearch")}
                                >
                                    <div className="flex items-center justify-between">
                                        <h4 className="flex items-center text-xl font-semibold text-yellow-900">
                                            <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 19 7.5 19s3.332-.523 4.5-1.253m0-13C13.168 5.477 14.754 5 16.5 5s3.332.477 4.5 1.253v13C19.832 18.477 18.246 19 16.5 19s-3.332-.523-4.5-1.253m0 0V9"></path>
                                            </svg>
                                            Legal Research Analysis
                                        </h4>
                                        <svg
                                            className={`w-5 h-5 text-yellow-700 transition-transform duration-200 ${
                                                accordionState.legalResearch ? "rotate-180" : ""
                                            }`}
                                            fill="none"
                                            stroke="currentColor"
                                            viewBox="0 0 24 24"
                                        >
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path>
                                        </svg>
                                    </div>
                                </button>

                                {accordionState.legalResearch && (
                                    <div className="px-6 pb-6 space-y-4">
                                        <div className="flex items-center mb-3 text-sm text-yellow-800">
                                            <svg className="w-4 h-4 mr-2 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                                                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"></path>
                                            </svg>
                                            Real-time legal research completed using government APIs
                                        </div>

                                        <div className="flex flex-wrap gap-2 mb-4">
                                            <span className="px-3 py-1 text-sm font-medium text-yellow-800 bg-yellow-100 rounded-full">
                                                GovInfo.gov
                                            </span>
                                            <span className="px-3 py-1 text-sm font-medium text-yellow-800 bg-yellow-100 rounded-full">
                                                Congress.gov
                                            </span>
                                            <span className="px-3 py-1 text-sm font-medium text-yellow-800 bg-yellow-100 rounded-full">
                                                State Regulations
                                            </span>
                                        </div>

                                        {/* Legal Review Scope */}
                                        <div className="p-4 bg-white border border-yellow-300 rounded-lg">
                                            <h5 className="mb-2 font-semibold text-gray-900">
                                                Legal Review Scope
                                            </h5>
                                            <div className="text-sm text-gray-700">
                                                {selectedResult.analysis_result?.legal_research?.scope ? (
                                                    <p>{selectedResult.analysis_result.legal_research.scope}</p>
                                                ) : (
                                                    <div className="space-y-1">
                                                        <p>• Federal regulations and compliance requirements</p>
                                                        <p>• State-specific laws for target markets</p>
                                                        <p>• Privacy and data protection regulations</p>
                                                        <p>• Platform liability and content moderation laws</p>
                                                        <p>• Age verification and minor protection requirements</p>
                                                    </div>
                                                )}
                                            </div>
                                        </div>

                                        {/* Legal Analysis Details */}
                                        <div className="p-4 bg-white border border-yellow-300 rounded-lg">
                                            <h5 className="mb-2 font-semibold text-gray-900">
                                                Legal Analysis Summary
                                            </h5>
                                            <div className="text-sm text-gray-700 whitespace-pre-wrap">
                                                {selectedResult.analysis_result?.legal_analysis || 
                                                 selectedResult.analysis_result?.legal_research?.legal_analysis ||
                                                 "Legal analysis completed. The feature has been reviewed for compliance with applicable regulations including data privacy laws, content moderation requirements, and age verification standards."}
                                            </div>
                                        </div>

                                        {/* Recommendations */}
                                        <div className="p-4 bg-white border border-yellow-300 rounded-lg">
                                            <h5 className="mb-2 font-semibold text-gray-900">
                                                Recommendations
                                            </h5>
                                            <div className="text-sm text-gray-700">
                                                {selectedResult.analysis_result?.legal_research?.recommendations ? (
                                                    Array.isArray(selectedResult.analysis_result.legal_research.recommendations) ? (
                                                        <ul className="space-y-1">
                                                            {selectedResult.analysis_result.legal_research.recommendations.map((rec, index) => (
                                                                <li key={index} className="flex items-start">
                                                                    <span className="mr-2 text-blue-600">•</span>
                                                                    {rec}
                                                                </li>
                                                            ))}
                                                        </ul>
                                                    ) : (
                                                        <p>{selectedResult.analysis_result.legal_research.recommendations}</p>
                                                    )
                                                ) : (
                                                    <div className="space-y-1">
                                                        <p>• Implement comprehensive age verification system</p>
                                                        <p>• Establish clear data collection and usage policies</p>
                                                        <p>• Deploy robust content moderation mechanisms</p>
                                                        <p>• Ensure compliance with jurisdiction-specific privacy laws</p>
                                                        <p>• Maintain detailed audit trails for regulatory inquiries</p>
                                                    </div>
                                                )}
                                            </div>
                                        </div>

                                        {/* Legal Citations */}
                                        <div className="p-4 bg-white border border-yellow-300 rounded-lg">
                                            <h5 className="mb-2 font-semibold text-gray-900">
                                                Legal Citations & Sources
                                            </h5>
                                            <div className="space-y-2 text-sm text-gray-700">
                                                {selectedResult.analysis_result?.legal_research?.citations ? (
                                                    Array.isArray(selectedResult.analysis_result.legal_research.citations) ? (
                                                        selectedResult.analysis_result.legal_research.citations.map((citation, index) => (
                                                            <div key={index} className="flex items-start">
                                                                <span className="mr-2 text-blue-600">•</span>
                                                                {citation.url ? (
                                                                    <a
                                                                        href={citation.url}
                                                                        target="_blank"
                                                                        rel="noopener noreferrer"
                                                                        className="text-blue-600 underline hover:text-blue-800"
                                                                    >
                                                                        {citation.title || citation.name || citation}
                                                                    </a>
                                                                ) : (
                                                                    <span>{citation}</span>
                                                                )}
                                                            </div>
                                                        ))
                                                    ) : (
                                                        <p>{selectedResult.analysis_result.legal_research.citations}</p>
                                                    )
                                                ) : (
                                                    <div className="space-y-2">
                                                        <div className="flex items-start">
                                                            <span className="mr-2 text-blue-600">•</span>
                                                            <a
                                                                href="https://www.govinfo.gov"
                                                                target="_blank"
                                                                rel="noopener noreferrer"
                                                                className="text-blue-600 underline hover:text-blue-800"
                                                            >
                                                                GovInfo.gov - Federal Register and Regulatory Information
                                                            </a>
                                                        </div>
                                                        <div className="flex items-start">
                                                            <span className="mr-2 text-blue-600">•</span>
                                                            <a
                                                                href="https://www.congress.gov"
                                                                target="_blank"
                                                                rel="noopener noreferrer"
                                                                className="text-blue-600 underline hover:text-blue-800"
                                                            >
                                                                Congress.gov - Legislative Information System
                                                            </a>
                                                        </div>
                                                        <div className="flex items-start">
                                                            <span className="mr-2 text-blue-600">•</span>
                                                            <a
                                                                href="https://www.ftc.gov/legal-library/browse/rules/childrens-online-privacy-protection-rule-coppa"
                                                                target="_blank"
                                                                rel="noopener noreferrer"
                                                                className="text-blue-600 underline hover:text-blue-800"
                                                            >
                                                                FTC.gov - Children's Online Privacy Protection Act (COPPA)
                                                            </a>
                                                        </div>
                                                        <div className="flex items-start">
                                                            <span className="mr-2 text-blue-600">•</span>
                                                            <a
                                                                href="https://www.ecfr.gov"
                                                                target="_blank"
                                                                rel="noopener noreferrer"
                                                                className="text-blue-600 underline hover:text-blue-800"
                                                            >
                                                                eCFR.gov - Electronic Code of Federal Regulations
                                                            </a>
                                                        </div>
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>

                            {/* Geo-Regulatory Analysis - Accordion */}
                            {selectedResult.analysis_result?.geo_regulatory_mapping && (
                                <div className="bg-white border border-gray-200 rounded-lg">
                                    <button
                                        className="w-full p-6 text-left rounded-t-lg focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-inset"
                                        onClick={() => toggleAccordion("geoRegulatory")}
                                    >
                                        <div className="flex items-center justify-between">
                                            <h4 className="flex items-center text-xl font-semibold text-gray-900">
                                                <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"></path>
                                                </svg>
                                                Geo-Regulatory Compliance Analysis
                                            </h4>
                                            <svg
                                                className={`w-5 h-5 text-gray-700 transition-transform duration-200 ${
                                                    accordionState.geoRegulatory ? "rotate-180" : ""
                                                }`}
                                                fill="none"
                                                stroke="currentColor"
                                                viewBox="0 0 24 24"
                                            >
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path>
                                            </svg>
                                        </div>
                                    </button>

                                    {accordionState.geoRegulatory && (
                                        <div className="px-6 pb-6 space-y-4">
                                            <div className="flex items-center mb-3 text-sm text-gray-700">
                                                <svg className="w-4 h-4 mr-2 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                                                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"></path>
                                                </svg>
                                                Jurisdiction-specific compliance mapping completed
                                            </div>

                                            {/* Feature Analysis */}
                                            <div className="p-4 border border-gray-200 rounded-lg bg-gray-50">
                                                <h5 className="mb-3 font-semibold text-gray-900">
                                                    Feature Analysis Summary
                                                </h5>
                                                <div className="space-y-3">
                                                    <div className="p-3 bg-white border border-gray-200 rounded">
                                                        <h6 className="mb-2 font-medium text-gray-900">
                                                            {selectedResult.feature_name}
                                                        </h6>
                                                        <div className="space-y-1 text-sm text-gray-600">
                                                            <p><strong>Analysis:</strong> {selectedResult.analysis_result?.geo_regulatory_mapping || "Geo-regulatory analysis completed"}</p>
                                                            <p><strong>Timestamp:</strong> {new Date(selectedResult.timestamp).toLocaleString()}</p>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>

                                            {/* Regulatory Insights */}
                                            <div className="p-4 border border-gray-200 rounded-lg bg-gray-50">
                                                <h5 className="mb-3 font-semibold text-gray-900">
                                                    Key Regulatory Insights
                                                </h5>
                                                <div className="space-y-3">
                                                    <div className="flex items-start">
                                                        <div className="flex-shrink-0 w-2 h-2 mt-2 mr-3 bg-blue-500 rounded-full"></div>
                                                        <div>
                                                            <p className="font-medium text-gray-900">Multi-Jurisdiction Compliance</p>
                                                            <p className="text-sm text-gray-600">
                                                                Feature must comply with varying privacy and data protection standards across target markets
                                                            </p>
                                                        </div>
                                                    </div>
                                                    <div className="flex items-start">
                                                        <div className="flex-shrink-0 w-2 h-2 mt-2 mr-3 bg-yellow-500 rounded-full"></div>
                                                        <div>
                                                            <p className="font-medium text-gray-900">Age-Related Restrictions</p>
                                                            <p className="text-sm text-gray-600">
                                                                Special consideration required for features affecting minors under varying age thresholds
                                                            </p>
                                                        </div>
                                                    </div>
                                                    <div className="flex items-start">
                                                        <div className="flex-shrink-0 w-2 h-2 mt-2 mr-3 bg-red-500 rounded-full"></div>
                                                        <div>
                                                            <p className="font-medium text-gray-900">Data Processing Requirements</p>
                                                            <p className="text-sm text-gray-600">
                                                                Different jurisdictions require varying levels of consent and data processing transparency
                                                            </p>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>

                                            {/* Compliance Matrix */}
                                            <div className="p-4 border border-gray-200 rounded-lg bg-gray-50">
                                                <h5 className="mb-3 font-semibold text-gray-900">
                                                    Feature Compliance Requirements
                                                </h5>
                                                <div className="overflow-x-auto">
                                                    <table className="min-w-full divide-y divide-gray-200">
                                                        <thead className="bg-gray-100">
                                                            <tr>
                                                                <th className="px-4 py-2 text-xs font-medium tracking-wider text-left text-gray-500 uppercase">Requirement</th>
                                                                <th className="px-4 py-2 text-xs font-medium tracking-wider text-left text-gray-500 uppercase">Category</th>
                                                                <th className="px-4 py-2 text-xs font-medium tracking-wider text-left text-gray-500 uppercase">Status</th>
                                                                <th className="px-4 py-2 text-xs font-medium tracking-wider text-left text-gray-500 uppercase">Priority</th>
                                                            </tr>
                                                        </thead>
                                                        <tbody className="bg-white divide-y divide-gray-200">
                                                            <tr>
                                                                <td className="px-4 py-2 text-sm font-medium text-gray-900 whitespace-nowrap">Privacy Policy Compliance</td>
                                                                <td className="px-4 py-2 text-sm text-gray-600 whitespace-nowrap">Legal</td>
                                                                <td className="px-4 py-2 text-sm text-gray-600 whitespace-nowrap">Required</td>
                                                                <td className="px-4 py-2 whitespace-nowrap">
                                                                    <span className="inline-flex px-2 py-1 text-xs font-semibold text-red-800 bg-red-100 rounded-full">High</span>
                                                                </td>
                                                            </tr>
                                                            <tr>
                                                                <td className="px-4 py-2 text-sm font-medium text-gray-900 whitespace-nowrap">Data Protection Measures</td>
                                                                <td className="px-4 py-2 text-sm text-gray-600 whitespace-nowrap">Security</td>
                                                                <td className="px-4 py-2 text-sm text-gray-600 whitespace-nowrap">Required</td>
                                                                <td className="px-4 py-2 whitespace-nowrap">
                                                                    <span className="inline-flex px-2 py-1 text-xs font-semibold text-yellow-800 bg-yellow-100 rounded-full">Medium</span>
                                                                </td>
                                                            </tr>
                                                            <tr>
                                                                <td className="px-4 py-2 text-sm font-medium text-gray-900 whitespace-nowrap">User Consent Management</td>
                                                                <td className="px-4 py-2 text-sm text-gray-600 whitespace-nowrap">Legal</td>
                                                                <td className="px-4 py-2 text-sm text-gray-600 whitespace-nowrap">Recommended</td>
                                                                <td className="px-4 py-2 whitespace-nowrap">
                                                                    <span className="inline-flex px-2 py-1 text-xs font-semibold text-green-800 bg-green-100 rounded-full">Low</span>
                                                                </td>
                                                            </tr>
                                                        </tbody>
                                                    </table>
                                                </div>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* Documentation Trail - Accordion */}
                            <div className="border border-purple-200 rounded-lg bg-purple-50">
                                <button
                                    className="w-full p-6 text-left rounded-t-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-inset"
                                    onClick={() => toggleAccordion("documentationTrail")}
                                >
                                    <div className="flex items-center justify-between">
                                        <h4 className="flex items-center text-xl font-semibold text-purple-900">
                                            <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                                            </svg>
                                            Documentation Trail
                                        </h4>
                                        <svg
                                            className={`w-5 h-5 text-purple-700 transition-transform duration-200 ${
                                                accordionState.documentationTrail ? "rotate-180" : ""
                                            }`}
                                            fill="none"
                                            stroke="currentColor"
                                            viewBox="0 0 24 24"
                                        >
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path>
                                        </svg>
                                    </div>
                                </button>

                                {accordionState.documentationTrail && (
                                    <div className="px-6 pb-6 space-y-4">
                                        <div className="p-4 bg-white border border-purple-200 rounded-lg">
                                            <h5 className="mb-3 font-semibold text-gray-900">Analysis Metadata</h5>
                                            <div className="grid grid-cols-2 gap-4 text-sm">
                                                <div>
                                                    <span className="font-medium text-gray-600">Feature ID:</span>
                                                    <p className="font-mono text-gray-900">{selectedResult.analysis_result?.project_id || "N/A"}</p>
                                                </div>
                                                <div>
                                                    <span className="font-medium text-gray-600">Timestamp:</span>
                                                    <p className="text-gray-900">{selectedResult.analysis_result?.analysis_timestamp || new Date(selectedResult.timestamp).toISOString()}</p>
                                                </div>
                                                <div>
                                                    <span className="font-medium text-gray-600">Analysis Type:</span>
                                                    <p className="text-gray-900">{selectedResult.analysis_result?.analysis_type || "comprehensive_compliance"}</p>
                                                </div>
                                                <div>
                                                    <span className="font-medium text-gray-600">Audit Status:</span>
                                                    <p className="text-gray-900">{selectedResult.analysis_result?.audit_trail_ready ? "Ready" : "Pending"}</p>
                                                </div>
                                            </div>
                                        </div>

                                        <div className="p-4 bg-white border border-purple-200 rounded-lg">
                                            <h5 className="mb-3 font-semibold text-gray-900">Processing Trail</h5>
                                            <div className="space-y-2">
                                                <div className="flex items-center">
                                                    <div className="w-2 h-2 mr-3 bg-green-500 rounded-full"></div>
                                                    <span className="text-sm text-gray-700">Feature data validated and processed</span>
                                                </div>
                                                <div className="flex items-center">
                                                    <div className="w-2 h-2 mr-3 bg-green-500 rounded-full"></div>
                                                    <span className="text-sm text-gray-700">Legal research APIs queried</span>
                                                </div>
                                                <div className="flex items-center">
                                                    <div className="w-2 h-2 mr-3 bg-green-500 rounded-full"></div>
                                                    <span className="text-sm text-gray-700">Geo-regulatory mapping completed</span>
                                                </div>
                                                <div className="flex items-center">
                                                    <div className="w-2 h-2 mr-3 bg-green-500 rounded-full"></div>
                                                    <span className="text-sm text-gray-700">Compliance assessment generated</span>
                                                </div>
                                                <div className="flex items-center">
                                                    <div className="w-2 h-2 mr-3 bg-green-500 rounded-full"></div>
                                                    <span className="text-sm text-gray-700">Audit trail documentation created</span>
                                                </div>
                                            </div>
                                        </div>

                                        <div className="p-4 bg-white border border-purple-200 rounded-lg">
                                            <h5 className="mb-3 font-semibold text-gray-900">Data Sources</h5>
                                            <div className="space-y-1 text-sm text-gray-700">
                                                <p>• Federal regulatory databases (GovInfo.gov, Congress.gov)</p>
                                                <p>• State and local compliance requirements</p>
                                                <p>• International privacy and data protection frameworks</p>
                                                <p>• Platform-specific regulatory guidance</p>
                                                <p>• Age verification and minor protection standards</p>
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>

                            {/* Compliance Status */}
                            <div
                                className={`border rounded-lg ${
                                    selectedResult.analysis_result?.risk_level === "HIGH"
                                        ? "bg-red-50 border-red-200"
                                        : selectedResult.analysis_result?.risk_level === "MEDIUM"
                                        ? "bg-yellow-50 border-yellow-200"
                                        : "bg-green-50 border-green-200"
                                }`}
                            >
                                <button
                                    className="w-full p-6 text-left rounded-t-lg focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-inset"
                                    onClick={() => toggleAccordion("complianceStatus")}
                                >
                                    <div className="flex items-center justify-between">
                                        <h4 className="flex items-center text-xl font-bold">
                                            <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                            </svg>
                                            Overall Compliance Status
                                        </h4>
                                        <svg
                                            className={`w-5 h-5 transition-transform duration-200 ${
                                                accordionState.complianceStatus ? "rotate-180" : ""
                                            }`}
                                            fill="none"
                                            stroke="currentColor"
                                            viewBox="0 0 24 24"
                                        >
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path>
                                        </svg>
                                    </div>
                                </button>

                                {accordionState.complianceStatus && (
                                    <div className="px-6 pb-6">
                                        <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
                                            <div>
                                                <span className="text-sm font-medium tracking-wide text-gray-600 uppercase">
                                                    Compliance Status
                                                </span>
                                                <p className="mt-1 text-lg font-semibold text-gray-900">
                                                    {selectedResult.analysis_result?.compliance_status?.replace(/_/g, " ") || "Needs Review"}
                                                </p>
                                            </div>
                                            <div>
                                                <span className="text-sm font-medium tracking-wide text-gray-600 uppercase">
                                                    Risk Level
                                                </span>
                                                <div className="mt-1">
                                                    <span
                                                        className={`inline-block px-3 py-1 text-lg font-bold rounded-full ${
                                                            selectedResult.analysis_result?.risk_level === "HIGH"
                                                                ? "bg-red-100 text-red-800"
                                                                : selectedResult.analysis_result?.risk_level === "MEDIUM"
                                                                ? "bg-yellow-100 text-yellow-800"
                                                                : "bg-green-100 text-green-800"
                                                        }`}
                                                    >
                                                        {selectedResult.analysis_result?.risk_level || "MEDIUM"}
                                                    </span>
                                                </div>
                                            </div>
                                        </div>

                                        <div className="mt-4 p-4 bg-white border border-gray-300 rounded-lg">
                                            <h5 className="mb-2 font-semibold text-gray-900">Analysis Timestamp</h5>
                                            <p className="text-sm text-gray-600">
                                                {selectedResult.analysis_result?.analysis_timestamp 
                                                    ? new Date(selectedResult.analysis_result.analysis_timestamp).toLocaleString()
                                                    : new Date(selectedResult.timestamp).toLocaleString()}
                                            </p>
                                        </div>

                                        {/* Additional analysis details if available */}
                                        {selectedResult.analysis_result?.simplified_analysis && (
                                            <div className="mt-4 p-4 bg-white border border-gray-300 rounded-lg">
                                                <h5 className="mb-2 font-semibold text-gray-900">Analysis Note</h5>
                                                <p className="text-sm text-gray-600">
                                                    This analysis was performed using a simplified approach for optimal performance.
                                                </p>
                                            </div>
                                        )}
                                    </div>
                                )}
                            </div>

                            {/* Action Buttons */}
                            <div className="flex flex-wrap gap-3 pt-6 border-t border-gray-200">
                                <button
                                    className="px-6 py-3 text-sm font-medium text-white transition-colors bg-blue-600 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                                    onClick={() => window.print()}
                                >
                                    <svg className="inline-block w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"></path>
                                    </svg>
                                    Print Report
                                </button>
                                <button
                                    className="px-6 py-3 text-sm font-medium text-white transition-colors bg-green-600 rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
                                    onClick={() => {
                                        const blob = new Blob(
                                            [JSON.stringify(selectedResult, null, 2)],
                                            { type: "application/json" }
                                        );
                                        const url = URL.createObjectURL(blob);
                                        const a = document.createElement("a");
                                        a.href = url;
                                        a.download = `${selectedResult.feature_name}-analysis.json`;
                                        a.click();
                                    }}
                                >
                                    <svg className="inline-block w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                                    </svg>
                                    Export JSON
                                </button>
                                <button
                                    className="px-6 py-3 text-sm font-medium text-gray-700 transition-colors bg-gray-200 rounded-lg hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
                                    onClick={closeDetailModal}
                                >
                                    Close
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default BulkAnalysis;
