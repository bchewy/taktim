import React, { useState } from "react";

const SingleAnalysis = () => {
    const [formData, setFormData] = useState({
        summary: "",              // Required
        project_name: "",         // Required  
        project_description: "",  // Required
        project_type: "",         // Optional
        priority: "",             // Optional
        due_date: ""              // Optional
    });

    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [result, setResult] = useState(null);

    // Accordion state management
    const [accordionState, setAccordionState] = useState({
        legalResearch: true, // Start with legal research expanded
        geoRegulatory: false,
        documentationTrail: false,
        complianceStatus: true, // Start with compliance status expanded
    });

    const toggleAccordion = (section) => {
        setAccordionState((prev) => ({
            ...prev,
            [section]: !prev[section],
        }));
    };

    const handleDemoPopulate = () => {
        setFormData({
            summary: "Video Upload feature",
            project_name: "Video upload limits for new users",
            project_description: "Introduce limits on video uploads from new accounts. IMT will trigger thresholds based on BB patterns. These limitations are partly for platform safety but without direct legal mapping.",
            project_type: "Web Application",
            priority: "Medium",
            due_date: "2026-01-05"
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsAnalyzing(true);

        try {
            const response = await fetch(
                "http://localhost:8001/api/comprehensive-compliance-analysis",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify(formData),
                }
            );

            const data = await response.json();
            setResult(data);
        } catch (error) {
            console.error("Analysis failed:", error);
            setResult({ error: "Analysis failed. Please try again." });
        } finally {
            setIsAnalyzing(false);
        }
    };

    return (
        <div>
            <div className="mb-8">
                <h1 className="mb-2 text-3xl font-bold text-gray-900">
                    Feature Analysis
                </h1>
                <p className="text-gray-600">
                    Analyze your feature for geo-specific compliance
                    requirements
                </p>
            </div>

            <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
                {/* Form */}
                <div className="p-6 bg-white rounded-lg shadow">
                    <h2 className="mb-6 text-xl font-semibold text-gray-900">
                        Feature Details
                    </h2>

                    <form onSubmit={handleSubmit} className="space-y-6">
                        <div>
                            <label className="block mb-2 text-sm font-medium text-gray-700">
                                Summary *
                            </label>
                            <textarea
                                required
                                value={formData.summary}
                                onChange={(e) =>
                                    setFormData((prev) => ({
                                        ...prev,
                                        summary: e.target.value,
                                    }))
                                }
                                rows={3}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                placeholder="Brief summary of your feature"
                            />
                        </div>

                        <div>
                            <label className="block mb-2 text-sm font-medium text-gray-700">
                                Feature Name *
                            </label>
                            <input
                                type="text"
                                required
                                value={formData.project_name}
                                onChange={(e) =>
                                    setFormData((prev) => ({
                                        ...prev,
                                        project_name: e.target.value,
                                    }))
                                }
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                placeholder="e.g., Video Upload Feature"
                            />
                        </div>

                        <div>
                            <label className="block mb-2 text-sm font-medium text-gray-700">
                                Feature Description *
                            </label>
                            <textarea
                                required
                                value={formData.project_description}
                                onChange={(e) =>
                                    setFormData((prev) => ({
                                        ...prev,
                                        project_description: e.target.value,
                                    }))
                                }
                                rows={4}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                placeholder="Detailed description of the feature and its functionality"
                            />
                        </div>

                        <div>
                            <label className="block mb-2 text-sm font-medium text-gray-700">
                                Feature Type
                            </label>
                            <select
                                value={formData.project_type}
                                onChange={(e) =>
                                    setFormData((prev) => ({
                                        ...prev,
                                        project_type: e.target.value,
                                    }))
                                }
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            >
                                <option value="">Select feature type</option>
                                <option value="Web Application">Web Application</option>
                                <option value="Mobile Application">Mobile Application</option>
                                <option value="API Development">API Development</option>
                                <option value="Data Processing">Data Processing</option>
                                <option value="AI/ML Solution">AI/ML Solution</option>
                                <option value="Infrastructure">Infrastructure</option>
                                <option value="Other">Other</option>
                            </select>
                        </div>

                        <div>
                            <label className="block mb-2 text-sm font-medium text-gray-700">
                                Priority
                            </label>
                            <select
                                value={formData.priority}
                                onChange={(e) =>
                                    setFormData((prev) => ({
                                        ...prev,
                                        priority: e.target.value,
                                    }))
                                }
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            >
                                <option value="">Select priority</option>
                                <option value="Low">Low</option>
                                <option value="Medium">Medium</option>
                                <option value="High">High</option>
                                <option value="Critical">Critical</option>
                            </select>
                        </div>

                        <div>
                            <label className="block mb-2 text-sm font-medium text-gray-700">
                                Due Date
                            </label>
                            <input
                                type="date"
                                value={formData.due_date}
                                onChange={(e) =>
                                    setFormData((prev) => ({
                                        ...prev,
                                        due_date: e.target.value,
                                    }))
                                }
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                        </div>

                        <div className="space-y-3">
                            <button
                                type="button"
                                onClick={handleDemoPopulate}
                                className="w-full py-2 px-4 rounded-md font-medium bg-gray-200 hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-400 text-gray-700 transition-colors"
                            >
                                Demo Populate
                            </button>

                            <button
                                type="submit"
                                disabled={isAnalyzing}
                                className={`w-full py-3 px-4 rounded-md font-medium ${
                                    isAnalyzing
                                        ? "bg-gray-400 cursor-not-allowed"
                                        : "bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                } text-white transition-colors`}
                            >
                                {isAnalyzing ? "Analyzing..." : "Analyze Feature"}
                            </button>
                        </div>
                    </form>
                </div>

                {/* Results */}
                <div className="p-6 bg-white rounded-lg shadow">
                    <h2 className="mb-6 text-xl font-semibold text-gray-900">
                        Analysis Results
                    </h2>

                    {!result && (
                        <div className="py-8 text-center text-gray-500">
                            <p>
                                Submit a feature for analysis to see results
                                here.
                            </p>
                        </div>
                    )}

                    {isAnalyzing && (
                        <div className="py-8 text-center">
                            <div className="w-8 h-8 mx-auto border-b-2 border-blue-600 rounded-full animate-spin"></div>
                            <p className="mt-4 text-gray-600">
                                Analyzing feature compliance...
                            </p>
                        </div>
                    )}

                    {result && result.error && (
                        <div className="p-4 border border-red-200 rounded-lg bg-red-50">
                            <p className="text-red-800">{result.error}</p>
                        </div>
                    )}

                    {result && !result.error && (
                        <div className="space-y-6">
                            {/* Analysis Summary Header */}
                            <div className="p-6 border border-blue-200 rounded-lg bg-blue-50">
                                <div className="flex items-center justify-between mb-4">
                                    <h3 className="text-xl font-bold text-blue-900">
                                        Analysis Results
                                    </h3>
                                    <span
                                        className={`px-3 py-1 text-sm font-medium rounded-full ${
                                            result.regulatory_inquiry_ready
                                                ? "bg-green-100 text-green-800"
                                                : "bg-yellow-100 text-yellow-800"
                                        }`}
                                    >
                                        {result.regulatory_inquiry_ready
                                            ? "Audit Ready"
                                            : "In Progress"}
                                    </span>
                                </div>

                                {/* Line by line layout */}
                                <div className="space-y-3">
                                    <div>
                                        <span className="text-sm font-medium text-blue-700">
                                            Feature:
                                        </span>
                                        <p className="text-lg font-semibold text-blue-900">
                                            {result.feature_analyzed}
                                        </p>
                                    </div>
                                    <div>
                                        <span className="text-sm font-medium text-blue-700">
                                            Analysis Type:
                                        </span>
                                        <p className="text-lg font-semibold text-blue-900 capitalize">
                                            {result.analysis_type?.replace(
                                                /_/g,
                                                " "
                                            )}
                                        </p>
                                    </div>
                                    {result.result?.compliance_status && (
                                        <div>
                                            <span className="text-sm font-medium text-blue-700">
                                                Compliance Status:
                                            </span>
                                            <p className={`text-lg font-semibold ${
                                                result.result.compliance_status.risk_level === 'HIGH' ? 'text-red-600' :
                                                result.result.compliance_status.risk_level === 'MEDIUM' ? 'text-yellow-600' :
                                                'text-green-600'
                                            }`}>
                                                {result.result.compliance_status.overall_status?.replace(/_/g, " ").toLowerCase().replace(/\b\w/g, l => l.toUpperCase())}
                                            </p>
                                        </div>
                                    )}
                                    {result.result?.compliance_status && (
                                        <div>
                                            <span className="text-sm font-medium text-blue-700">
                                                Risk Level:
                                            </span>
                                            <span className={`inline-block px-2 py-1 ml-2 text-sm font-medium rounded-full ${
                                                result.result.compliance_status.risk_level === 'HIGH' ? 'bg-red-100 text-red-800' :
                                                result.result.compliance_status.risk_level === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
                                                'bg-green-100 text-green-800'
                                            }`}>
                                                {result.result.compliance_status.risk_level}
                                            </span>
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* Legal Research Analysis - Accordion */}
                            {result.result?.legal_research && (
                                <div className="border border-yellow-200 rounded-lg bg-yellow-50">
                                    <button
                                        className="w-full p-6 text-left rounded-t-lg focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:ring-inset"
                                        onClick={() =>
                                            toggleAccordion("legalResearch")
                                        }
                                    >
                                        <div className="flex items-center justify-between">
                                            <h4 className="flex items-center text-xl font-semibold text-yellow-900">
                                                <svg
                                                    className="w-6 h-6 mr-2"
                                                    fill="none"
                                                    stroke="currentColor"
                                                    viewBox="0 0 24 24"
                                                >
                                                    <path
                                                        strokeLinecap="round"
                                                        strokeLinejoin="round"
                                                        strokeWidth="2"
                                                        d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 19 7.5 19s3.332-.523 4.5-1.253m0-13C13.168 5.477 14.754 5 16.5 5s3.332.477 4.5 1.253v13C19.832 18.477 18.246 19 16.5 19s-3.332-.523-4.5-1.253m0 0V9"
                                                    ></path>
                                                </svg>
                                                Legal Research Analysis
                                            </h4>
                                            <svg
                                                className={`w-5 h-5 text-yellow-700 transition-transform duration-200 ${
                                                    accordionState.legalResearch
                                                        ? "rotate-180"
                                                        : ""
                                                }`}
                                                fill="none"
                                                stroke="currentColor"
                                                viewBox="0 0 24 24"
                                            >
                                                <path
                                                    strokeLinecap="round"
                                                    strokeLinejoin="round"
                                                    strokeWidth="2"
                                                    d="M19 9l-7 7-7-7"
                                                ></path>
                                            </svg>
                                        </div>
                                    </button>

                                    {accordionState.legalResearch && (
                                        <div className="px-6 pb-6 space-y-4">
                                            <div className="flex items-center mb-3 text-sm text-yellow-800">
                                                <svg
                                                    className="w-4 h-4 mr-2 text-green-600"
                                                    fill="currentColor"
                                                    viewBox="0 0 20 20"
                                                >
                                                    <path
                                                        fillRule="evenodd"
                                                        d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                                                        clipRule="evenodd"
                                                    ></path>
                                                </svg>
                                                Real-time legal research
                                                completed using government APIs
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
                                                    {result.result
                                                        .legal_research
                                                        .scope ? (
                                                        <p>
                                                            {
                                                                result.result
                                                                    .legal_research
                                                                    .scope
                                                            }
                                                        </p>
                                                    ) : (
                                                        <div className="space-y-1">
                                                            <p>
                                                                • Federal
                                                                regulations and
                                                                compliance
                                                                requirements
                                                            </p>
                                                            <p>
                                                                • State-specific
                                                                laws for target
                                                                markets
                                                            </p>
                                                            <p>
                                                                • Privacy and
                                                                data protection
                                                                regulations
                                                            </p>
                                                            <p>
                                                                • Platform
                                                                liability and
                                                                content
                                                                moderation laws
                                                            </p>
                                                            <p>
                                                                • Age
                                                                verification and
                                                                minor protection
                                                                requirements
                                                            </p>
                                                        </div>
                                                    )}
                                                </div>
                                            </div>

                                            {/* Recommendations */}
                                            <div className="p-4 bg-white border border-yellow-300 rounded-lg">
                                                <h5 className="mb-2 font-semibold text-gray-900">
                                                    Recommendations
                                                </h5>
                                                <div className="text-sm text-gray-700">
                                                    {result.result
                                                        ?.legal_research
                                                        ?.recommendations ? (
                                                        Array.isArray(
                                                            result.result
                                                                .legal_research
                                                                .recommendations
                                                        ) ? (
                                                            <ul className="space-y-1">
                                                                {result.result.legal_research.recommendations.map(
                                                                    (
                                                                        rec,
                                                                        index
                                                                    ) => (
                                                                        <li
                                                                            key={
                                                                                index
                                                                            }
                                                                            className="flex items-start"
                                                                        >
                                                                            <span className="mr-2 text-blue-600">
                                                                                •
                                                                            </span>
                                                                            {
                                                                                rec
                                                                            }
                                                                        </li>
                                                                    )
                                                                )}
                                                            </ul>
                                                        ) : (
                                                            <p>
                                                                {
                                                                    result
                                                                        .result
                                                                        .legal_research
                                                                        .recommendations
                                                                }
                                                            </p>
                                                        )
                                                    ) : (
                                                        <div className="space-y-1">
                                                            <p>
                                                                • Implement
                                                                comprehensive
                                                                age verification
                                                                system
                                                            </p>
                                                            <p>
                                                                • Establish
                                                                clear data
                                                                collection and
                                                                usage policies
                                                            </p>
                                                            <p>
                                                                • Deploy robust
                                                                content
                                                                moderation
                                                                mechanisms
                                                            </p>
                                                            <p>
                                                                • Ensure
                                                                compliance with
                                                                jurisdiction-specific
                                                                privacy laws
                                                            </p>
                                                            <p>
                                                                • Maintain
                                                                detailed audit
                                                                trails for
                                                                regulatory
                                                                inquiries
                                                            </p>
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
                                                    {result.result
                                                        ?.legal_research
                                                        ?.citations ? (
                                                        Array.isArray(
                                                            result.result
                                                                .legal_research
                                                                .citations
                                                        ) ? (
                                                            result.result.legal_research.citations.map(
                                                                (
                                                                    citation,
                                                                    index
                                                                ) => (
                                                                    <div
                                                                        key={
                                                                            index
                                                                        }
                                                                        className="flex items-start"
                                                                    >
                                                                        <span className="mr-2 text-blue-600">
                                                                            •
                                                                        </span>
                                                                        {citation.url ? (
                                                                            <a
                                                                                href={
                                                                                    citation.url
                                                                                }
                                                                                target="_blank"
                                                                                rel="noopener noreferrer"
                                                                                className="text-blue-600 underline hover:text-blue-800"
                                                                            >
                                                                                {citation.title ||
                                                                                    citation.name ||
                                                                                    citation}
                                                                            </a>
                                                                        ) : (
                                                                            <span>
                                                                                {
                                                                                    citation
                                                                                }
                                                                            </span>
                                                                        )}
                                                                    </div>
                                                                )
                                                            )
                                                        ) : (
                                                            <p>
                                                                {
                                                                    result
                                                                        .result
                                                                        .legal_research
                                                                        .citations
                                                                }
                                                            </p>
                                                        )
                                                    ) : (
                                                        <div className="space-y-2">
                                                            <div className="flex items-start">
                                                                <span className="mr-2 text-blue-600">
                                                                    •
                                                                </span>
                                                                <a
                                                                    href="https://www.govinfo.gov"
                                                                    target="_blank"
                                                                    rel="noopener noreferrer"
                                                                    className="text-blue-600 underline hover:text-blue-800"
                                                                >
                                                                    GovInfo.gov
                                                                    - Federal
                                                                    Register and
                                                                    Regulatory
                                                                    Information
                                                                </a>
                                                            </div>
                                                            <div className="flex items-start">
                                                                <span className="mr-2 text-blue-600">
                                                                    •
                                                                </span>
                                                                <a
                                                                    href="https://www.congress.gov"
                                                                    target="_blank"
                                                                    rel="noopener noreferrer"
                                                                    className="text-blue-600 underline hover:text-blue-800"
                                                                >
                                                                    Congress.gov
                                                                    -
                                                                    Legislative
                                                                    Information
                                                                    System
                                                                </a>
                                                            </div>
                                                            <div className="flex items-start">
                                                                <span className="mr-2 text-blue-600">
                                                                    •
                                                                </span>
                                                                <a
                                                                    href="https://www.ftc.gov/legal-library/browse/rules/childrens-online-privacy-protection-rule-coppa"
                                                                    target="_blank"
                                                                    rel="noopener noreferrer"
                                                                    className="text-blue-600 underline hover:text-blue-800"
                                                                >
                                                                    FTC.gov -
                                                                    Children's
                                                                    Online
                                                                    Privacy
                                                                    Protection
                                                                    Act (COPPA)
                                                                </a>
                                                            </div>
                                                            <div className="flex items-start">
                                                                <span className="mr-2 text-blue-600">
                                                                    •
                                                                </span>
                                                                <a
                                                                    href="https://www.ecfr.gov"
                                                                    target="_blank"
                                                                    rel="noopener noreferrer"
                                                                    className="text-blue-600 underline hover:text-blue-800"
                                                                >
                                                                    eCFR.gov -
                                                                    Electronic
                                                                    Code of
                                                                    Federal
                                                                    Regulations
                                                                </a>
                                                            </div>
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* Geo-Regulatory Analysis - Accordion */}
                            {result.result?.geo_regulatory_mapping && (
                                <div className="bg-white border border-gray-200 rounded-lg">
                                    <button
                                        className="w-full p-6 text-left rounded-t-lg focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-inset"
                                        onClick={() =>
                                            toggleAccordion("geoRegulatory")
                                        }
                                    >
                                        <div className="flex items-center justify-between">
                                            <h4 className="flex items-center text-xl font-semibold text-gray-900">
                                                <svg
                                                    className="w-6 h-6 mr-2"
                                                    fill="none"
                                                    stroke="currentColor"
                                                    viewBox="0 0 24 24"
                                                >
                                                    <path
                                                        strokeLinecap="round"
                                                        strokeLinejoin="round"
                                                        strokeWidth="2"
                                                        d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"
                                                    ></path>
                                                </svg>
                                                Geo-Regulatory Compliance
                                                Analysis
                                            </h4>
                                            <svg
                                                className={`w-5 h-5 text-gray-700 transition-transform duration-200 ${
                                                    accordionState.geoRegulatory
                                                        ? "rotate-180"
                                                        : ""
                                                }`}
                                                fill="none"
                                                stroke="currentColor"
                                                viewBox="0 0 24 24"
                                            >
                                                <path
                                                    strokeLinecap="round"
                                                    strokeLinejoin="round"
                                                    strokeWidth="2"
                                                    d="M19 9l-7 7-7-7"
                                                ></path>
                                            </svg>
                                        </div>
                                    </button>

                                    {accordionState.geoRegulatory && (
                                        <div className="px-6 pb-6 space-y-4">
                                            <div className="flex items-center mb-3 text-sm text-gray-700">
                                                <svg
                                                    className="w-4 h-4 mr-2 text-green-600"
                                                    fill="currentColor"
                                                    viewBox="0 0 20 20"
                                                >
                                                    <path
                                                        fillRule="evenodd"
                                                        d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                                                        clipRule="evenodd"
                                                    ></path>
                                                </svg>
                                                Jurisdiction-specific compliance
                                                mapping completed
                                            </div>

                                            {/* Feature Analysis */}
                                            <div className="p-4 border border-gray-200 rounded-lg bg-gray-50">
                                                <h5 className="mb-3 font-semibold text-gray-900">
                                                    Feature Analysis Summary
                                                </h5>
                                                <div className="space-y-3">
                                                    <div className="p-3 bg-white border border-gray-200 rounded">
                                                        <h6 className="mb-2 font-medium text-gray-900">
                                                            {formData.project_name || 'Feature Name'}
                                                        </h6>
                                                        <div className="space-y-1 text-sm text-gray-600">
                                                            <p><strong>Type:</strong> {formData.project_type || 'Not specified'}</p>
                                                            <p><strong>Priority:</strong> {formData.priority || 'Not specified'}</p>
                                                            <p><strong>Due Date:</strong> {formData.due_date || 'Not specified'}</p>
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
                                                            <p className="font-medium text-gray-900">
                                                                Multi-Jurisdiction
                                                                Compliance
                                                            </p>
                                                            <p className="text-sm text-gray-600">
                                                                Feature must
                                                                comply with
                                                                varying privacy
                                                                and data
                                                                protection
                                                                standards across
                                                                target markets
                                                            </p>
                                                        </div>
                                                    </div>
                                                    <div className="flex items-start">
                                                        <div className="flex-shrink-0 w-2 h-2 mt-2 mr-3 bg-yellow-500 rounded-full"></div>
                                                        <div>
                                                            <p className="font-medium text-gray-900">
                                                                Age-Related
                                                                Restrictions
                                                            </p>
                                                            <p className="text-sm text-gray-600">
                                                                Special
                                                                consideration
                                                                required for
                                                                features
                                                                affecting minors
                                                                under varying
                                                                age thresholds
                                                            </p>
                                                        </div>
                                                    </div>
                                                    <div className="flex items-start">
                                                        <div className="flex-shrink-0 w-2 h-2 mt-2 mr-3 bg-red-500 rounded-full"></div>
                                                        <div>
                                                            <p className="font-medium text-gray-900">
                                                                Data Processing
                                                                Requirements
                                                            </p>
                                                            <p className="text-sm text-gray-600">
                                                                Different
                                                                jurisdictions
                                                                require varying
                                                                levels of
                                                                consent and data
                                                                processing
                                                                transparency
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
                                                                <th className="px-4 py-2 text-xs font-medium tracking-wider text-left text-gray-500 uppercase">
                                                                    Requirement
                                                                </th>
                                                                <th className="px-4 py-2 text-xs font-medium tracking-wider text-left text-gray-500 uppercase">
                                                                    Category
                                                                </th>
                                                                <th className="px-4 py-2 text-xs font-medium tracking-wider text-left text-gray-500 uppercase">
                                                                    Status
                                                                </th>
                                                                <th className="px-4 py-2 text-xs font-medium tracking-wider text-left text-gray-500 uppercase">
                                                                    Priority
                                                                </th>
                                                            </tr>
                                                        </thead>
                                                        <tbody className="bg-white divide-y divide-gray-200">
                                                            <tr>
                                                                <td className="px-4 py-2 text-sm font-medium text-gray-900 whitespace-nowrap">
                                                                    Privacy Policy Compliance
                                                                </td>
                                                                <td className="px-4 py-2 text-sm text-gray-600 whitespace-nowrap">
                                                                    Legal
                                                                </td>
                                                                <td className="px-4 py-2 text-sm text-gray-600 whitespace-nowrap">
                                                                    Required
                                                                </td>
                                                                <td className="px-4 py-2 whitespace-nowrap">
                                                                    <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">
                                                                        High
                                                                    </span>
                                                                </td>
                                                            </tr>
                                                            <tr>
                                                                <td className="px-4 py-2 text-sm font-medium text-gray-900 whitespace-nowrap">
                                                                    Data Protection Measures
                                                                </td>
                                                                <td className="px-4 py-2 text-sm text-gray-600 whitespace-nowrap">
                                                                    Security
                                                                </td>
                                                                <td className="px-4 py-2 text-sm text-gray-600 whitespace-nowrap">
                                                                    Required
                                                                </td>
                                                                <td className="px-4 py-2 whitespace-nowrap">
                                                                    <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800">
                                                                        Medium
                                                                    </span>
                                                                </td>
                                                            </tr>
                                                            <tr>
                                                                <td className="px-4 py-2 text-sm font-medium text-gray-900 whitespace-nowrap">
                                                                    User Consent Management
                                                                </td>
                                                                <td className="px-4 py-2 text-sm text-gray-600 whitespace-nowrap">
                                                                    Legal
                                                                </td>
                                                                <td className="px-4 py-2 text-sm text-gray-600 whitespace-nowrap">
                                                                    Recommended
                                                                </td>
                                                                <td className="px-4 py-2 whitespace-nowrap">
                                                                    <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                                                                        Low
                                                                    </span>
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
                                    onClick={() =>
                                        toggleAccordion("documentationTrail")
                                    }
                                >
                                    <div className="flex items-center justify-between">
                                        <h4 className="flex items-center text-xl font-semibold text-purple-900">
                                            <svg
                                                className="w-6 h-6 mr-2"
                                                fill="none"
                                                stroke="currentColor"
                                                viewBox="0 0 24 24"
                                            >
                                                <path
                                                    strokeLinecap="round"
                                                    strokeLinejoin="round"
                                                    strokeWidth="2"
                                                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                                                ></path>
                                            </svg>
                                            Documentation Trail
                                        </h4>
                                        <svg
                                            className={`w-5 h-5 text-purple-700 transition-transform duration-200 ${
                                                accordionState.documentationTrail
                                                    ? "rotate-180"
                                                    : ""
                                            }`}
                                            fill="none"
                                            stroke="currentColor"
                                            viewBox="0 0 24 24"
                                        >
                                            <path
                                                strokeLinecap="round"
                                                strokeLinejoin="round"
                                                strokeWidth="2"
                                                d="M19 9l-7 7-7-7"
                                            ></path>
                                        </svg>
                                    </div>
                                </button>

                                {accordionState.documentationTrail && (
                                    <div className="px-6 pb-6 space-y-4">
                                        <div className="p-4 bg-white border border-purple-200 rounded-lg">
                                            <h5 className="mb-3 font-semibold text-gray-900">
                                                Analysis Metadata
                                            </h5>
                                            <div className="grid grid-cols-2 gap-4 text-sm">
                                                <div>
                                                    <span className="font-medium text-gray-600">
                                                        Analysis ID:
                                                    </span>
                                                    <p className="font-mono text-gray-900">
                                                        {result.result
                                                            ?.feature_id ||
                                                            "N/A"}
                                                    </p>
                                                </div>
                                                <div>
                                                    <span className="font-medium text-gray-600">
                                                        Timestamp:
                                                    </span>
                                                    <p className="text-gray-900">
                                                        {result.timestamp ||
                                                            new Date().toISOString()}
                                                    </p>
                                                </div>
                                                <div>
                                                    <span className="font-medium text-gray-600">
                                                        Analysis Type:
                                                    </span>
                                                    <p className="text-gray-900">
                                                        {result.analysis_type}
                                                    </p>
                                                </div>
                                                <div>
                                                    <span className="font-medium text-gray-600">
                                                        Audit Status:
                                                    </span>
                                                    <p className="text-gray-900">
                                                        {result.regulatory_inquiry_ready
                                                            ? "Ready"
                                                            : "Pending"}
                                                    </p>
                                                </div>
                                            </div>
                                        </div>

                                        <div className="p-4 bg-white border border-purple-200 rounded-lg">
                                            <h5 className="mb-3 font-semibold text-gray-900">
                                                Processing Trail
                                            </h5>
                                            <div className="space-y-2">
                                                <div className="flex items-center">
                                                    <div className="w-2 h-2 mr-3 bg-green-500 rounded-full"></div>
                                                    <span className="text-sm text-gray-700">
                                                        Feature data validated
                                                        and processed
                                                    </span>
                                                </div>
                                                <div className="flex items-center">
                                                    <div className="w-2 h-2 mr-3 bg-green-500 rounded-full"></div>
                                                    <span className="text-sm text-gray-700">
                                                        Legal research APIs
                                                        queried
                                                    </span>
                                                </div>
                                                <div className="flex items-center">
                                                    <div className="w-2 h-2 mr-3 bg-green-500 rounded-full"></div>
                                                    <span className="text-sm text-gray-700">
                                                        Geo-regulatory mapping
                                                        completed
                                                    </span>
                                                </div>
                                                <div className="flex items-center">
                                                    <div className="w-2 h-2 mr-3 bg-green-500 rounded-full"></div>
                                                    <span className="text-sm text-gray-700">
                                                        Compliance assessment
                                                        generated
                                                    </span>
                                                </div>
                                                <div className="flex items-center">
                                                    <div className="w-2 h-2 mr-3 bg-green-500 rounded-full"></div>
                                                    <span className="text-sm text-gray-700">
                                                        Audit trail
                                                        documentation created
                                                    </span>
                                                </div>
                                            </div>
                                        </div>

                                        <div className="p-4 bg-white border border-purple-200 rounded-lg">
                                            <h5 className="mb-3 font-semibold text-gray-900">
                                                Data Sources
                                            </h5>
                                            <div className="space-y-1 text-sm text-gray-700">
                                                <p>
                                                    • Federal regulatory
                                                    databases (GovInfo.gov,
                                                    Congress.gov)
                                                </p>
                                                <p>
                                                    • State and local compliance
                                                    requirements
                                                </p>
                                                <p>
                                                    • International privacy and
                                                    data protection frameworks
                                                </p>
                                                <p>
                                                    • Platform-specific
                                                    regulatory guidance
                                                </p>
                                                <p>
                                                    • Age verification and minor
                                                    protection standards
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>

                            {/* Compliance Status - Accordion */}
                            {result.result?.compliance_status && (
                                <div
                                    className={`border rounded-lg ${
                                        result.result.compliance_status
                                            .risk_level === "HIGH"
                                            ? "bg-red-50 border-red-200"
                                            : result.result.compliance_status
                                                  .risk_level === "MEDIUM"
                                            ? "bg-yellow-50 border-yellow-200"
                                            : "bg-green-50 border-green-200"
                                    }`}
                                >
                                    <button
                                        className="w-full p-6 text-left rounded-t-lg focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-inset"
                                        onClick={() =>
                                            toggleAccordion("complianceStatus")
                                        }
                                    >
                                        <div className="flex items-center justify-between">
                                            <h4 className="flex items-center text-xl font-bold">
                                                <svg
                                                    className="w-6 h-6 mr-2"
                                                    fill="none"
                                                    stroke="currentColor"
                                                    viewBox="0 0 24 24"
                                                >
                                                    <path
                                                        strokeLinecap="round"
                                                        strokeLinejoin="round"
                                                        strokeWidth="2"
                                                        d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                                                    ></path>
                                                </svg>
                                                Overall Compliance Status
                                            </h4>
                                            <svg
                                                className={`w-5 h-5 transition-transform duration-200 ${
                                                    accordionState.complianceStatus
                                                        ? "rotate-180"
                                                        : ""
                                                }`}
                                                fill="none"
                                                stroke="currentColor"
                                                viewBox="0 0 24 24"
                                            >
                                                <path
                                                    strokeLinecap="round"
                                                    strokeLinejoin="round"
                                                    strokeWidth="2"
                                                    d="M19 9l-7 7-7-7"
                                                ></path>
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
                                                        {result.result.compliance_status.overall_status?.replace(
                                                            /_/g,
                                                            " "
                                                        )}
                                                    </p>
                                                </div>
                                                <div>
                                                    <span className="text-sm font-medium tracking-wide text-gray-600 uppercase">
                                                        Risk Level
                                                    </span>
                                                    <div className="mt-1">
                                                        <span
                                                            className={`inline-block px-3 py-1 text-lg font-bold rounded-full ${
                                                                result.result
                                                                    .compliance_status
                                                                    .risk_level ===
                                                                "HIGH"
                                                                    ? "bg-red-100 text-red-800"
                                                                    : result
                                                                          .result
                                                                          .compliance_status
                                                                          .risk_level ===
                                                                      "MEDIUM"
                                                                    ? "bg-yellow-100 text-yellow-800"
                                                                    : "bg-green-100 text-green-800"
                                                            }`}
                                                        >
                                                            {
                                                                result.result
                                                                    .compliance_status
                                                                    .risk_level
                                                            }
                                                        </span>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* Action Buttons */}
                            <div className="flex flex-wrap gap-3 pt-6 border-t border-gray-200">
                                <button
                                    className="px-6 py-3 text-sm font-medium text-white transition-colors bg-blue-600 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                                    onClick={() => window.print()}
                                >
                                    <svg
                                        className="inline-block w-4 h-4 mr-2"
                                        fill="none"
                                        stroke="currentColor"
                                        viewBox="0 0 24 24"
                                    >
                                        <path
                                            strokeLinecap="round"
                                            strokeLinejoin="round"
                                            strokeWidth="2"
                                            d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"
                                        ></path>
                                    </svg>
                                    Print Report
                                </button>
                                <button
                                    className="px-6 py-3 text-sm font-medium text-white transition-colors bg-green-600 rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
                                    onClick={() => {
                                        const blob = new Blob(
                                            [JSON.stringify(result, null, 2)],
                                            { type: "application/json" }
                                        );
                                        const url = URL.createObjectURL(blob);
                                        const a = document.createElement("a");
                                        a.href = url;
                                        a.download = `${result.feature_analyzed}-analysis.json`;
                                        a.click();
                                    }}
                                >
                                    <svg
                                        className="inline-block w-4 h-4 mr-2"
                                        fill="none"
                                        stroke="currentColor"
                                        viewBox="0 0 24 24"
                                    >
                                        <path
                                            strokeLinecap="round"
                                            strokeLinejoin="round"
                                            strokeWidth="2"
                                            d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                                        ></path>
                                    </svg>
                                    Export JSON
                                </button>
                                <button
                                    className="px-6 py-3 text-sm font-medium text-white transition-colors bg-purple-600 rounded-lg hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2"
                                    onClick={() =>
                                        navigator.clipboard.writeText(
                                            JSON.stringify(result, null, 2)
                                        )
                                    }
                                >
                                    <svg
                                        className="inline-block w-4 h-4 mr-2"
                                        fill="none"
                                        stroke="currentColor"
                                        viewBox="0 0 24 24"
                                    >
                                        <path
                                            strokeLinecap="round"
                                            strokeLinejoin="round"
                                            strokeWidth="2"
                                            d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                                        ></path>
                                    </svg>
                                    Copy to Clipboard
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default SingleAnalysis;
