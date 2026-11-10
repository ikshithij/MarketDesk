export type Source={id:string;title:string;url:string;publisher:string;published_at:string|null;access:'read'|'search_result';primary:boolean};
export type Finding={text:string;kind:'reported'|'derived'|'interpretation';source_ids:string[]};
export type ReportSection={id:string;title:string;summary:string;findings:Finding[];gaps:string[]};
export type Report={headline:string;summary:string;business_in_one_sentence:string;research_view:string;bull_case:string[];bear_case:string[];sections:ReportSection[];sources:Source[];limitations:string[];predictive_status:string;screening_review?:{status:string;summary:string;checks:{metric:string;reported_value:number|null;unit:string;period:string;source_ids:string[];note:string}[]}};
export type ResearchRun={id:string;symbol:string;name:string;focus:string;status:'queued'|'running'|'complete'|'failed';stage:string;error:string|null;created_at:string;updated_at:string;standard_version:string;engine_version:string;context?:any;report?:Report|null;engine?:any};
export type Choice={symbol:string;name:string;exchange?:string;sector:string};
