import { Component, OnInit, Input, ViewChild } from '@angular/core';
import { ApiRoutes, HttpService, UtilService, AlertMessages } from '../../shared';
import { Router } from '@angular/router';
import { MatPaginator, MatTableDataSource, MatSort } from '@angular/material';
@Component({
  selector: 'app-automl',
  templateUrl: './automl.component.html',
  styleUrls: ['./automl.component.scss']
})
export class AutomlComponent implements OnInit {
  @Input() dataSource: any = {};
  dataAutomlSource: any;
  problem_type: any;
  displayedColumns: string[] = [
    'position',
    'variable',
    'dtype',
    'missing_val',
    'changedataType',
    'imputation_methods',
    'data_transformation_steps',
    'use_for_model',
    'target_variable'
  ];
  target_variable: any;
  displayAutoMLPrametersForm = false;
  reqPayload: any = {
    data: [
      {
        'variable': 'mpg',
        'changedataType': 'Continuous',
        'imputation_method': '',
        'data_transformation_steps': '',
        'use_for_model': true
      },
      {
        'variable': 'cylinders',
        'changedataType': 'Continuous',
        'imputation_method': '',
        'data_transformation_steps': '',
        'use_for_model': false
      }
    ],
    problem_type: 'Regression/Classification',
    target_variable: 'mpg'
  };
  public fromDefaultData: any = {};
  supervised = true;
  @ViewChild(MatPaginator) paginator: MatPaginator;
  @ViewChild(MatSort) sort: MatSort;
  pageSize = 10;
  pageSizeOptions = [10, 25, 100];
  isLoading = false;
  constructor(private apiService: HttpService, private router: Router, private utilService: UtilService) { }

  ngOnInit() {
    this.autoMLPaginationSorting();
  }

  onAutoMLTrainingFormDataSubmit(formData: any) {
    this.displayAutoMLPrametersForm = false;
    this.isLoading = true;
    const payload = {
      data: this.dataSource.data,
      problem_type: this.problem_type,
      target_variable: this.target_variable,
      idforData: this.dataSource.idforData,
      newPMMLFileName: `${formData.model_name}`,
      filePath: this.dataSource.selectedData.url,
      parameters: formData
    };
    console.log(payload);
    const options = {
      body: payload
    };
    const apiEndpoint = this.supervised ? ApiRoutes.dataAutoML(this.dataSource.selectedData.id) : ApiRoutes.dataAutoMLAnomaly(this.dataSource.selectedData.id);
    this.apiService.request(ApiRoutes.methods.POST, apiEndpoint, options)
      .subscribe(data => {
        console.log(data);
        this.utilService.alert(AlertMessages.AUTOML.train);
        this.router.navigate(['tasks']);
      });
  }
  build() {
    this.fromDefaultData = this.dataSource.options;
    this.fromDefaultData.problem_type = this.problem_type;
    this.fromDefaultData.supervised = this.supervised;
    this.displayAutoMLPrametersForm = true;
  }

  /**
   * The function is for generating client side pagination and sorting
   */
  autoMLPaginationSorting() {
    this.dataAutomlSource = new MatTableDataSource(this.dataSource.data);
    this.dataAutomlSource.paginator = this.paginator;
    this.dataAutomlSource.sort = this.sort;
  }
}
