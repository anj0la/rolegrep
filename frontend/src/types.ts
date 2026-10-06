export interface Card {id:string;title:string|null;company:string|null;location:string|null;arrangement:string|null;level:string|null;technologies:string[];posted_at:string|null;discovered_at:string;source:string;score:number|null;eligibility:string}
export interface Decision {
 job:{id:string;title:string|null;company:string|null;description:string;location:string|null;arrangement:string|null;level:string|null;education:string|null;salary:string|null;deadline:string|null;cover_letter:string|null;posted_at:string|null;application_url:string|null;experience:{kind:string;minimum:number|null;wording:string}[];conflicts:{field:string;values:string[];evidence:string[]}[];limitations:string[];sources:{provider:string;submitted_url:string|null;fetched_at:string;snapshot:string;content_hash:string}[]};
 eligibility:{status:string;reasons:string[]};
 match:{overall:number|null;qualification:number|null;personal:number;explanation:string;strong:string[];partial:string[];gaps:string[];concerns:string[];candidate_version:string;algorithm_version:string};
}
