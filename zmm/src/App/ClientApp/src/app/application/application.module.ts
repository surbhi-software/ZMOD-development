import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { SharedModule } from './../shared';
import { MonacoEditorModule } from 'ngx-monaco-editor';
import { NgxDnDModule } from '@swimlane/ngx-dnd';

import { ApplicationComponent } from './application.component';
import { ApplicationRouting } from './application.routing';

import { UsersComponent } from './users/users.component';
import { DataComponent } from './data/data.component';
import { EditorComponent } from './editor/editor.component';
import { ProfileComponent } from './profile/profile.component';
import { ModelsComponent } from './models/models.component';
import { CodeComponent } from './code/code.component';
import { SidebarComponent } from './sidebar/sidebar.component';
import { ContentSidenavDemoComponent } from './content-sidenav-demo/content-sidenav-demo.component';
import { HeaderComponent } from './header/header.component';
import { FooterComponent } from './footer/footer.component';
import { AutomlComponent } from './automl/automl.component';
import { TasksComponent } from './tasks/tasks.component';
import { FilterPanelComponent } from './filter-panel/filter-panel.component';
import { TrainingParametersFormComponent } from './models/training-parameters-form/training-parameters-form.component';
import { CumulocityComponent } from './cumulocity/cumulocity.component';
import { AutomlParametersFormComponent } from './automl/automl-parameters-form/automl-parameters-form.component';
import { CompileParameterFormComponent } from './models/compile-parameter-form/compile-parameter-form.component';
import { AssetsComponent } from './assets/assets.component';
import { DisplayConfigFormComponent } from './assets/display-config-form/display-config-form.component';
import { WeldingConfigFormComponent } from './data/welding-config-form/welding-config-form.component';
import { LicenseComponent } from './license/license.component';
import { ExcuteFormComponent } from './code/excute-form/excute-form.component';
import { CronEditorModule } from 'cron-editor';
import { RepoComponent } from './repo/repo.component';
import { SettingsComponent } from './settings/settings.component';

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    ApplicationRouting,
    NgbModule,
    SharedModule,
    MonacoEditorModule.forRoot(),
    NgxDnDModule,
    CronEditorModule
  ],
  declarations: [
    ApplicationComponent,
    UsersComponent,
    DataComponent,
    EditorComponent,
    ProfileComponent,
    ModelsComponent,
    CodeComponent,
    SidebarComponent,
    ContentSidenavDemoComponent,
    HeaderComponent,
    FooterComponent,
    AutomlComponent,
    TasksComponent,
    FilterPanelComponent,
    TrainingParametersFormComponent,
    CumulocityComponent,
    AutomlParametersFormComponent,
    CompileParameterFormComponent,
    AssetsComponent,
    DisplayConfigFormComponent,
    WeldingConfigFormComponent,
    LicenseComponent,
    ExcuteFormComponent,
    RepoComponent,
    SettingsComponent
  ]
})
export class ApplicationModule { }
