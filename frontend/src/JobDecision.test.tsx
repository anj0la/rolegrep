// @vitest-environment jsdom
import {afterEach,expect,it} from 'vitest';
import {cleanup,render,screen} from '@testing-library/react';
import {JobDecision} from './JobDecision';
import type {Decision} from './types';
afterEach(cleanup);
it('labels provisional matching and surfaces uncertainty without rendering source HTML',()=>{
 const decision:Decision={job:{id:'test',title:'Junior developer',company:null,description:'<script>bad()</script>',location:null,arrangement:null,level:null,education:null,salary:null,deadline:null,cover_letter:null,posted_at:null,application_url:null,experience:[],conflicts:[{field:'arrangement',values:['Remote','Hybrid'],evidence:['Remote or hybrid']}],limitations:['Review source'],sources:[]},eligibility:{status:'uncertain',reasons:['Experience unknown']},match:{overall:70,qualification:70,personal:70,explanation:'Synthetic fixture only',strong:[],partial:[],gaps:[],concerns:[],candidate_version:'test',algorithm_version:'test'}};
 const {container}=render(<JobDecision decision={decision}/>);
 expect(screen.getByText('70% provisional fixture match')).toBeTruthy();
 expect(screen.getByText('Experience unknown')).toBeTruthy();
 expect(screen.getByText('Review conflict: arrangement')).toBeTruthy();
 expect(container.querySelector('script')).toBeNull();
});
