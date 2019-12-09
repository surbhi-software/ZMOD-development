import { Component, OnInit, Input, Output, EventEmitter, OnChanges } from '@angular/core';
import { ApiRoutes, HttpService, UtilService } from '../../shared';
import { finalize } from 'rxjs/operators';

@Component({
  selector: 'app-filter-panel',
  templateUrl: './filter-panel.component.html',
  styleUrls: ['./filter-panel.component.scss']
})
export class FilterPanelComponent implements OnInit, OnChanges {
  @Input() option: any;
  @Output() close = new EventEmitter<any>();
  @Output() selected = new EventEmitter<any>();
  data: any = [];
  selectedData: any = {};
  public isLoading = false;
  public filter: any = '';
  constructor(private apiService: HttpService, public utilService: UtilService) { }

  ngOnInit() {
  }
  closeFilter() {
    this.close.emit(true);
  }
  submit() {
    this.selected.emit(this.selectedData);
  }

  ngOnChanges() {
    console.log(this.option);
    let options = {};
    options = {
      params: this.option.params
    };
    this.loadData(this.option.route, options);
  }

  loadData(route: string, options: any) {
    this.isLoading = true;
    this.apiService.request(ApiRoutes.methods.GET, route, options).pipe(finalize(() => {
      this.isLoading = false;
    }))
      .subscribe(data => {
        if (data && data.length) {
          this.data = data;
        }
      });
  }

  selectData(data: any) {
    this.selectedData = data;
    if (this.option.params && this.option.params.server) {
      this.selectedData.server = this.option.params.server;
    }
  }
}
