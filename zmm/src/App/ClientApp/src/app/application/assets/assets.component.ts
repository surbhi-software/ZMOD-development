import { Component, OnInit, Input } from '@angular/core';
import { ApiRoutes, HttpService, UtilService, AlertMessages } from '../../shared';
import { finalize } from 'rxjs/operators';

@Component({
  selector: 'app-assets',
  templateUrl: './assets.component.html',
  styleUrls: ['./assets.component.scss']
})
export class AssetsComponent implements OnInit {


  constructor(private apiService: HttpService, private utilService: UtilService) { }

  public filter: any = '';
  public isLoading = false;
  public listOfInstances: any = [];
  public isContentLoading = false;
  public selectedInstance: any = {};
  public showFormPanel = false;

  /**
   * It is used for getting all the instances
   */
  public getAllInstances() {
    this.isLoading = true;
    this.apiService.request(ApiRoutes.methods.GET, ApiRoutes.instance)
      .pipe(finalize(() => {
        this.isLoading = false;
      }))
      .subscribe(response => {
        this.listOfInstances = response;
        // select first record by default
        if (response && response.length) {
          this.viewInstance(response[0]);
        }
      });
  }

  /**
   * It is used for viewing each instance
   * @param data : Instance
   */
  public viewInstance(data: any) {
    this.selectedInstance = data;
  }
  public toggleSidebar(action: string) {
    this.utilService.toggleSidebar(action);
  }
  ngOnInit() {
    this.getAllInstances();
  }

  /**
   * It is used for killing the particular instance
   * @param instanceId : instance id
   */
  public killInstance() {
    this.isLoading = true;
    this.apiService.request(ApiRoutes.methods.DELETE, ApiRoutes.instanceKill(this.selectedInstance.id))
      .pipe(finalize(() => {
        this.isLoading = false;
      }
      ))
      .subscribe(response => {
        this.getAllInstances();
        this.utilService.alert(AlertMessages.INSTANCE.shutDown);

      });
  }

  public displayInstanceForm() {
    this.showFormPanel = true;
  }
  onDisplayConfigFormSubmit(formData: any) {
    this.showFormPanel = false;
    formData.type = 'ZMK';
    const options = {
      body: formData
    };
    this.apiService.request(ApiRoutes.methods.POST, ApiRoutes.instance, options)
      .subscribe(data => {
        console.log(data);
        this.getAllInstances();
        this.utilService.alert(AlertMessages.INSTANCE.instanceForm);
      });
  }
}
